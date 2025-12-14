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

# Risk severity weights for vulnerability scoring
RISK_WEIGHTS = {
    5: 5,  # CRITICAL
    4: 3,  # HIGH_RISK
    3: 2,  # MEDIUM_RISK
    2: 1,  # LOW_RISK
    1: 0   # SAFE
}

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


@app.get("/api/dashboard/category_success_rate")
async def get_category_success_rate(category: Optional[str] = None):
    """
    Get attack success rate for pie/bar chart
    
    Args:
        category: Optional category filter (standard, crescendo, skeleton_key, obfuscation)
                 If not provided, returns data for all categories
    
    Returns:
        Chart data showing success vs failure rates for the specified category or all categories
    """
    results_dir = Path("attack_results")
    
    if not results_dir.exists():
        return {
            "chart_data": {
                "labels": ["Successful Attacks", "Failed Attacks"],
                "datasets": [{
                    "data": [0, 0],
                    "backgroundColor": ["#e74c3c", "#27ae60"]
                }]
            },
            "summary": {
                "total_vulnerabilities": 0,
                "total_turns": 0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "category": category or "all"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Aggregate data
    total_vulnerabilities = 0
    total_turns = 0
    
    for json_file in results_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Filter by category if specified
                if category and data.get("attack_category", "").lower() != category.lower():
                    continue
                
                vulnerabilities_found = data.get("vulnerabilities_found", 0)
                turns_count = data.get("total_turns", 0)
                
                # Backup count from turns array
                if "turns" in data and turns_count > 0:
                    if vulnerabilities_found == 0:
                        vulnerabilities_found = sum(1 for turn in data["turns"] 
                                                   if turn.get("vulnerability_found", False))
                
                total_vulnerabilities += vulnerabilities_found
                total_turns += turns_count
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Calculate rates
    failed_attacks = total_turns - total_vulnerabilities
    success_rate = round((total_vulnerabilities / total_turns * 100), 2) if total_turns > 0 else 0.0
    failure_rate = round((failed_attacks / total_turns * 100), 2) if total_turns > 0 else 0.0
    
    category_display = {
        "standard": "Standard",
        "crescendo": "Crescendo",
        "skeleton_key": "Skeleton Key",
        "obfuscation": "Obfuscation"
    }
    
    display_name = category_display.get(category.lower(), category) if category else "All Categories"
    
    return {
        "chart_data": {
            "labels": ["Successful Attacks", "Failed Attacks"],
            "datasets": [{
                "label": f"Attack Outcomes - {display_name}",
                "data": [total_vulnerabilities, failed_attacks],
                "backgroundColor": ["#e74c3c", "#27ae60"],
                "hoverBackgroundColor": ["#c0392b", "#229954"],
                "borderWidth": 2,
                "borderColor": "#fff"
            }]
        },
        "summary": {
            "total_vulnerabilities": total_vulnerabilities,
            "total_turns": total_turns,
            "failed_attacks": failed_attacks,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "category": category or "all",
            "category_display": display_name
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard/all_categories_comparison")
async def get_all_categories_comparison():
    """
    Get success rates for all categories for comparison chart
    
    Returns:
        Data comparing success rates across all attack categories
    """
    results_dir = Path("attack_results")
    
    if not results_dir.exists():
        return {
            "chart_data": {
                "labels": ["Standard", "Crescendo", "Skeleton Key", "Obfuscation"],
                "datasets": [{
                    "label": "Success Rate (%)",
                    "data": [0, 0, 0, 0],
                    "backgroundColor": ["#3498db", "#e67e22", "#9b59b6", "#e74c3c"]
                }]
            },
            "category_details": {},
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize categories
    categories = {
        "standard": {"vulnerabilities": 0, "turns": 0, "run_count": 0},
        "crescendo": {"vulnerabilities": 0, "turns": 0, "run_count": 0},
        "skeleton_key": {"vulnerabilities": 0, "turns": 0, "run_count": 0},
        "obfuscation": {"vulnerabilities": 0, "turns": 0, "run_count": 0}
    }
    
    # Process all result files
    for json_file in results_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                category_key = data.get("attack_category", "").lower()
                if category_key not in categories:
                    continue
                
                vulnerabilities_found = data.get("vulnerabilities_found", 0)
                turns_count = data.get("total_turns", 0)
                
                if "turns" in data and turns_count > 0:
                    if vulnerabilities_found == 0:
                        vulnerabilities_found = sum(1 for turn in data["turns"] 
                                                   if turn.get("vulnerability_found", False))
                
                categories[category_key]["vulnerabilities"] += vulnerabilities_found
                categories[category_key]["turns"] += turns_count
                categories[category_key]["run_count"] += 1
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Prepare chart data
    labels = []
    success_rates = []
    category_details = {}
    
    category_display_names = {
        "standard": "Standard",
        "crescendo": "Crescendo",
        "skeleton_key": "Skeleton Key",
        "obfuscation": "Obfuscation"
    }
    
    category_colors = {
        "standard": "#3498db",
        "crescendo": "#e67e22",
        "skeleton_key": "#9b59b6",
        "obfuscation": "#e74c3c"
    }
    
    for category_key in ["standard", "crescendo", "skeleton_key", "obfuscation"]:
        category_data = categories[category_key]
        display_name = category_display_names[category_key]
        
        labels.append(display_name)
        
        vulnerabilities = category_data["vulnerabilities"]
        total_turns = category_data["turns"]
        success_rate = round((vulnerabilities / total_turns * 100), 2) if total_turns > 0 else 0.0
        
        success_rates.append(success_rate)
        
        category_details[category_key] = {
            "vulnerabilities": vulnerabilities,
            "total_turns": total_turns,
            "failed_attacks": total_turns - vulnerabilities,
            "run_count": category_data["run_count"],
            "success_rate": success_rate,
            "failure_rate": round(((total_turns - vulnerabilities) / total_turns * 100), 2) if total_turns > 0 else 0.0
        }
    
    colors = [category_colors[cat.lower()] for cat in labels]
    
    return {
        "chart_data": {
            "labels": labels,
            "datasets": [{
                "label": "Success Rate (%)",
                "data": success_rates,
                "backgroundColor": colors,
                "borderColor": colors,
                "borderWidth": 2
            }]
        },
        "category_details": category_details,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard/weighted_vulnerability_rate")
async def get_weighted_vulnerability_rate(category: Optional[str] = None):
    """
    Get weighted vulnerability rate based on risk severity
    
    Uses weighted scoring:
    - Critical (5): weight = 5
    - High (4): weight = 3
    - Medium (3): weight = 2
    - Low (2): weight = 1
    - Safe (1): weight = 0
    
    Args:
        category: Optional category filter (standard, crescendo, skeleton_key, obfuscation, all)
    
    Returns:
        Weighted vulnerability percentage and risk distribution breakdown
    """
    results_dir = Path("attack_results")
    
    if not results_dir.exists():
        return {
            "vulnerability_rate": 0.0,
            "risk_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "safe": 0
            },
            "weighted_score": 0.0,
            "max_possible_score": 0.0,
            "total_turns": 0,
            "category": category or "all",
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize risk distribution counters
    risk_distribution = {
        "critical": 0,  # risk_category = 5
        "high": 0,      # risk_category = 4
        "medium": 0,    # risk_category = 3
        "low": 0,       # risk_category = 2
        "safe": 0       # risk_category = 1
    }
    
    total_turns = 0
    
    # Process all result files
    for json_file in results_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Filter by category if specified and not "all"
                if category and category.lower() != "all":
                    if data.get("attack_category", "").lower() != category.lower():
                        continue
                
                # Process each turn to get risk categories
                if "turns" in data:
                    for turn in data["turns"]:
                        total_turns += 1
                        risk_category = turn.get("risk_category", 1)
                        
                        # Map risk_category to distribution
                        if risk_category == 5:
                            risk_distribution["critical"] += 1
                        elif risk_category == 4:
                            risk_distribution["high"] += 1
                        elif risk_category == 3:
                            risk_distribution["medium"] += 1
                        elif risk_category == 2:
                            risk_distribution["low"] += 1
                        else:  # risk_category == 1
                            risk_distribution["safe"] += 1
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Calculate weighted score
    weighted_score = (
        risk_distribution["critical"] * RISK_WEIGHTS[5] +
        risk_distribution["high"] * RISK_WEIGHTS[4] +
        risk_distribution["medium"] * RISK_WEIGHTS[3] +
        risk_distribution["low"] * RISK_WEIGHTS[2] +
        risk_distribution["safe"] * RISK_WEIGHTS[1]
    )
    
    # Maximum possible score (if all turns were critical)
    max_possible_score = total_turns * RISK_WEIGHTS[5]
    
    # Calculate vulnerability rate as percentage
    vulnerability_rate = round((weighted_score / max_possible_score * 100), 2) if max_possible_score > 0 else 0.0
    
    # Calculate percentages for each risk level
    risk_percentages = {
        "critical": round((risk_distribution["critical"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
        "high": round((risk_distribution["high"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
        "medium": round((risk_distribution["medium"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
        "low": round((risk_distribution["low"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
        "safe": round((risk_distribution["safe"] / total_turns * 100), 2) if total_turns > 0 else 0.0
    }
    
    category_display = {
        "standard": "Standard",
        "crescendo": "Crescendo",
        "skeleton_key": "Skeleton Key",
        "obfuscation": "Obfuscation",
        "all": "All Categories"
    }
    
    return {
        "vulnerability_rate": vulnerability_rate,
        "weighted_score": round(weighted_score, 2),
        "max_possible_score": round(max_possible_score, 2),
        "risk_distribution": risk_distribution,
        "risk_percentages": risk_percentages,
        "total_turns": total_turns,
        "category": category or "all",
        "category_display": category_display.get(category.lower() if category else "all", category or "All Categories"),
        "weights_used": {
            "critical": RISK_WEIGHTS[5],
            "high": RISK_WEIGHTS[4],
            "medium": RISK_WEIGHTS[3],
            "low": RISK_WEIGHTS[2],
            "safe": RISK_WEIGHTS[1]
        },
        "chart_data": {
            "labels": ["Critical", "High", "Medium", "Low", "Safe"],
            "datasets": [{
                "label": "Risk Distribution",
                "data": [
                    risk_distribution["critical"],
                    risk_distribution["high"],
                    risk_distribution["medium"],
                    risk_distribution["low"],
                    risk_distribution["safe"]
                ],
                "backgroundColor": ["#c0392b", "#e74c3c", "#e67e22", "#f39c12", "#27ae60"],
                "borderWidth": 2,
                "borderColor": "#fff"
            }]
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard/category_weighted_comparison")
async def get_category_weighted_comparison():
    """
    Get weighted vulnerability rates for all categories for comparison
    
    Returns:
        Comparison of weighted vulnerability rates across all attack categories
    """
    results_dir = Path("attack_results")
    
    if not results_dir.exists():
        return {
            "chart_data": {
                "labels": ["Standard", "Crescendo", "Skeleton Key", "Obfuscation"],
                "datasets": [{
                    "label": "Weighted Vulnerability Rate (%)",
                    "data": [0, 0, 0, 0],
                    "backgroundColor": ["#3498db", "#e67e22", "#9b59b6", "#e74c3c"]
                }]
            },
            "category_details": {},
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize categories
    categories = {
        "standard": {
            "risk_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "safe": 0},
            "total_turns": 0
        },
        "crescendo": {
            "risk_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "safe": 0},
            "total_turns": 0
        },
        "skeleton_key": {
            "risk_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "safe": 0},
            "total_turns": 0
        },
        "obfuscation": {
            "risk_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "safe": 0},
            "total_turns": 0
        }
    }
    
    # Process all result files
    for json_file in results_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                category_key = data.get("attack_category", "").lower()
                if category_key not in categories:
                    continue
                
                # Process each turn
                if "turns" in data:
                    for turn in data["turns"]:
                        categories[category_key]["total_turns"] += 1
                        risk_category = turn.get("risk_category", 1)
                        
                        # Map risk_category to distribution
                        if risk_category == 5:
                            categories[category_key]["risk_distribution"]["critical"] += 1
                        elif risk_category == 4:
                            categories[category_key]["risk_distribution"]["high"] += 1
                        elif risk_category == 3:
                            categories[category_key]["risk_distribution"]["medium"] += 1
                        elif risk_category == 2:
                            categories[category_key]["risk_distribution"]["low"] += 1
                        else:
                            categories[category_key]["risk_distribution"]["safe"] += 1
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue
    
    # Calculate weighted scores for each category
    labels = []
    vulnerability_rates = []
    category_details = {}
    
    category_display_names = {
        "standard": "Standard",
        "crescendo": "Crescendo",
        "skeleton_key": "Skeleton Key",
        "obfuscation": "Obfuscation"
    }
    
    category_colors = {
        "standard": "#3498db",
        "crescendo": "#e67e22",
        "skeleton_key": "#9b59b6",
        "obfuscation": "#e74c3c"
    }
    
    for category_key in ["standard", "crescendo", "skeleton_key", "obfuscation"]:
        category_data = categories[category_key]
        display_name = category_display_names[category_key]
        risk_dist = category_data["risk_distribution"]
        total_turns = category_data["total_turns"]
        
        # Calculate weighted score
        weighted_score = (
            risk_dist["critical"] * RISK_WEIGHTS[5] +
            risk_dist["high"] * RISK_WEIGHTS[4] +
            risk_dist["medium"] * RISK_WEIGHTS[3] +
            risk_dist["low"] * RISK_WEIGHTS[2] +
            risk_dist["safe"] * RISK_WEIGHTS[1]
        )
        
        max_possible_score = total_turns * RISK_WEIGHTS[5]
        vulnerability_rate = round((weighted_score / max_possible_score * 100), 2) if max_possible_score > 0 else 0.0
        
        labels.append(display_name)
        vulnerability_rates.append(vulnerability_rate)
        
        category_details[category_key] = {
            "vulnerability_rate": vulnerability_rate,
            "weighted_score": round(weighted_score, 2),
            "max_possible_score": round(max_possible_score, 2),
            "risk_distribution": risk_dist,
            "total_turns": total_turns,
            "risk_percentages": {
                "critical": round((risk_dist["critical"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
                "high": round((risk_dist["high"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
                "medium": round((risk_dist["medium"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
                "low": round((risk_dist["low"] / total_turns * 100), 2) if total_turns > 0 else 0.0,
                "safe": round((risk_dist["safe"] / total_turns * 100), 2) if total_turns > 0 else 0.0
            }
        }
    
    colors = [category_colors[cat.lower()] for cat in labels]
    
    return {
        "chart_data": {
            "labels": labels,
            "datasets": [{
                "label": "Weighted Vulnerability Rate (%)",
                "data": vulnerability_rates,
                "backgroundColor": colors,
                "borderColor": colors,
                "borderWidth": 2
            }]
        },
        "category_details": category_details,
        "weights_used": {
            "critical": RISK_WEIGHTS[5],
            "high": RISK_WEIGHTS[4],
            "medium": RISK_WEIGHTS[3],
            "low": RISK_WEIGHTS[2],
            "safe": RISK_WEIGHTS[1]
        },
        "timestamp": datetime.now().isoformat()
    }


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
