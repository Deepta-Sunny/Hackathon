"""
FastAPI Backend for Red Team Attack Orchestration
Provides REST API and WebSocket endpoints for real-time attack monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import WebSocket broadcast utilities
from core import websocket_broadcast

from core.orchestrator import ThreeRunCrescendoOrchestrator
from core.crescendo_orchestrator import CrescendoAttackOrchestrator
from core.skeleton_key_orchestrator import SkeletonKeyAttackOrchestrator
from core.obfuscation_orchestrator import ObfuscationAttackOrchestrator

# Initialize FastAPI app
app = FastAPI(
    title="Red Team Attack Orchestrator",
    description="AI-powered security testing platform with real-time monitoring",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

# Global attack state
attack_state = {
    "running": False,
    "current_category": None,
    "current_run": None,
    "current_turn": None,
    "total_categories": 4,
    "total_runs_per_category": 3,
    "results": {}
}


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")


manager = ConnectionManager()


# Set the manager for websocket_broadcast module
websocket_broadcast.set_manager(manager)


# Global function for orchestrators to broadcast logs
async def broadcast_attack_log(message: dict):
    """Global function for orchestrators to broadcast real-time logs"""
    await manager.broadcast(message)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Red Team Attack Orchestrator",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/status")
async def get_status():
    """Get current attack status"""
    return {
        "attack_state": attack_state,
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/attack/start")
async def start_attack(
    websocket_url: str = Form(...),
    architecture_file: UploadFile = File(...)
):
    """
    Start automated multi-category attack campaign
    
    Args:
        websocket_url: Target chatbot WebSocket URL
        architecture_file: Architecture .md file describing target system
    """
    
    if attack_state["running"]:
        raise HTTPException(status_code=400, detail="Attack already running")
    
    # Save uploaded architecture file
    arch_filename = f"uploads/architecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    os.makedirs("uploads", exist_ok=True)
    
    with open(arch_filename, "wb") as f:
        content = await architecture_file.read()
        f.write(content)
    
    # Update attack state
    attack_state["running"] = True
    attack_state["websocket_url"] = websocket_url
    attack_state["architecture_file"] = arch_filename
    attack_state["start_time"] = datetime.now().isoformat()
    
    # Broadcast start message
    await manager.broadcast({
        "type": "attack_started",
        "data": {
            "websocket_url": websocket_url,
            "architecture_file": architecture_file.filename,
            "timestamp": datetime.now().isoformat()
        }
    })
    
    # Start attack in background
    asyncio.create_task(execute_attack_campaign(websocket_url, arch_filename))
    
    return {
        "status": "started",
        "message": "Attack campaign initiated",
        "websocket_url": websocket_url,
        "architecture_file": architecture_file.filename
    }


@app.post("/api/attack/stop")
async def stop_attack():
    """Stop ongoing attack campaign"""
    if not attack_state["running"]:
        raise HTTPException(status_code=400, detail="No attack is running")
    
    attack_state["running"] = False
    
    await manager.broadcast({
        "type": "attack_stopped",
        "data": {
            "timestamp": datetime.now().isoformat()
        }
    })
    
    return {"status": "stopped", "message": "Attack campaign stopped"}


@app.get("/api/results")
async def get_results():
    """Get all attack results"""
    results_dir = Path("attack_results")
    
    if not results_dir.exists():
        return {"results": []}
    
    results = []
    for json_file in results_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            results.append({
                "filename": json_file.name,
                "attack_category": data.get("attack_category"),
                "run_number": data.get("run_number"),
                "vulnerabilities_found": data.get("vulnerabilities_found"),
                "total_turns": data.get("total_turns"),
                "start_time": data.get("start_time"),
                "end_time": data.get("end_time")
            })
    
    return {"results": results}


@app.get("/api/results/{category}/{run_number}")
async def get_run_result(category: str, run_number: int):
    """Get detailed results for specific run"""
    filename = f"attack_results/{category}_attack_run_{run_number}.json"
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Run result not found")
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data


@app.websocket("/ws/attack-monitor")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attack monitoring
    Broadcasts turn-by-turn updates to connected frontends
    """
    await manager.connect(websocket)
    
    try:
        # Send current state immediately
        await manager.send_personal({
            "type": "connection_established",
            "data": {
                "attack_state": attack_state,
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
        
        # Keep connection alive
        while True:
            # Receive messages from client (heartbeat, etc.)
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await manager.send_personal({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        manager.disconnect(websocket)


async def execute_attack_campaign(websocket_url: str, architecture_file: str):
    """Execute the full multi-category attack campaign with real-time updates"""
    
    attack_modes = ["standard", "crescendo", "skeleton_key", "obfuscation"]
    
    mode_names = {
        "standard": "Standard Attack",
        "crescendo": "Crescendo Attack",
        "skeleton_key": "Skeleton Key Attack",
        "obfuscation": "Obfuscation Attack"
    }
    
    all_reports = {}
    
    try:
        for idx, attack_mode in enumerate(attack_modes, 1):
            attack_state["current_category"] = attack_mode
            attack_state["category_progress"] = f"{idx}/{len(attack_modes)}"
            
            # Broadcast category start
            await manager.broadcast({
                "type": "category_started",
                "data": {
                    "category": attack_mode,
                    "category_name": mode_names[attack_mode],
                    "progress": f"{idx}/{len(attack_modes)}",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # Create orchestrator
            if attack_mode == "obfuscation":
                from config.settings import OBFUSCATION_RUNS, OBFUSCATION_TURNS_PER_RUN
                orchestrator = ObfuscationAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=architecture_file,
                    total_runs=OBFUSCATION_RUNS,
                    turns_per_run=OBFUSCATION_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_obfuscation_assessment()
            elif attack_mode == "skeleton_key":
                from config.settings import SKELETON_KEY_RUNS, SKELETON_KEY_TURNS_PER_RUN
                orchestrator = SkeletonKeyAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=architecture_file,
                    total_runs=SKELETON_KEY_RUNS,
                    turns_per_run=SKELETON_KEY_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_skeleton_key_assessment()
            elif attack_mode == "crescendo":
                from config.settings import CRESCENDO_RUNS, CRESCENDO_TURNS_PER_RUN
                orchestrator = CrescendoAttackOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=architecture_file,
                    total_runs=CRESCENDO_RUNS,
                    turns_per_run=CRESCENDO_TURNS_PER_RUN
                )
                final_report = await orchestrator.execute_crescendo_assessment()
            else:
                orchestrator = ThreeRunCrescendoOrchestrator(
                    websocket_url=websocket_url,
                    architecture_file=architecture_file
                )
                final_report = await orchestrator.execute_full_assessment()
            
            all_reports[attack_mode] = final_report
            
            # Broadcast category completion
            await manager.broadcast({
                "type": "category_completed",
                "data": {
                    "category": attack_mode,
                    "category_name": mode_names[attack_mode],
                    "vulnerabilities": final_report.get('total_vulnerabilities', 0),
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        # Campaign complete
        attack_state["running"] = False
        attack_state["end_time"] = datetime.now().isoformat()
        attack_state["results"] = all_reports
        
        await manager.broadcast({
            "type": "campaign_completed",
            "data": {
                "total_categories": len(attack_modes),
                "results": all_reports,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        attack_state["running"] = False
        attack_state["error"] = str(e)
        
        await manager.broadcast({
            "type": "error",
            "data": {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        })


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║   RED TEAM ATTACK ORCHESTRATOR - FastAPI Backend                  ║
    ║                                                                    ║
    ║   Real-time WebSocket Monitoring                                   ║
    ║   RESTful API for Attack Control                                   ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
