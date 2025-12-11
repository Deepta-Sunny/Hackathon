# Red Team Attack Orchestrator - Setup Guide

## Backend Setup

### 1. Install FastAPI Dependencies

```bash
cd C:\RedTeaming\BACKEND
pip install -r requirements_api.txt
```

### 2. Start Backend Server

```bash
cd C:\RedTeaming\BACKEND
python api_server.py
```

The backend will start on: **http://localhost:8080**

### API Endpoints

- **GET** `/` - Health check
- **GET** `/api/status` - Get current attack status
- **POST** `/api/attack/start` - Start attack campaign (multipart/form-data)
  - `websocket_url`: Target WebSocket URL (form field)
  - `architecture_file`: Architecture .md file (file upload)
- **POST** `/api/attack/stop` - Stop ongoing attack
- **GET** `/api/results` - Get all attack results
- **GET** `/api/results/{category}/{run_number}` - Get specific run details
- **WebSocket** `/ws/attack-monitor` - Real-time attack monitoring

## Frontend Setup

### 1. Open Frontend

Simply open `C:\RedTeaming\FRONTEND\index.html` in your web browser.

Or use a simple HTTP server:

```bash
cd C:\RedTeaming\FRONTEND
python -m http.server 3000
```

Then open: **http://localhost:3000**

### 2. Configure Attack

1. Enter target WebSocket URL (e.g., `ws://localhost:8001`)
2. Upload architecture .md file
3. Click "🚀 Start Attack Campaign"

### 3. Monitor Attacks

- **Real-time WebSocket updates** show progress
- **Category tabs** separate different attack types
- **Run cards** display statistics for each run (3 runs per category)
- **Turn log** shows detailed turn-by-turn information

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│  (Browser - Real-time WebSocket Connection)              │
│  - Attack configuration                                  │
│  - Real-time monitoring                                  │
│  - Results visualization                                 │
└──────────────┬──────────────────────────────────────────┘
               │
               │ WebSocket (ws://localhost:8080/ws/attack-monitor)
               │ REST API (http://localhost:8080/api/*)
               │
┌──────────────▼──────────────────────────────────────────┐
│                   FASTAPI BACKEND                        │
│  (Python - api_server.py)                                │
│  - Attack orchestration                                  │
│  - WebSocket broadcasting                                │
│  - File upload handling                                  │
│  - Result management                                     │
└──────────────┬──────────────────────────────────────────┘
               │
               │ Executes orchestrators
               │
┌──────────────▼──────────────────────────────────────────┐
│              ATTACK ORCHESTRATORS                        │
│  - StandardAttack (3 runs × 25 turns)                    │
│  - CrescendoAttack (3 runs × 15 turns)                   │
│  - SkeletonKeyAttack (3 runs × 10 turns)                 │
│  - ObfuscationAttack (3 runs × 20 turns)                 │
└──────────────┬──────────────────────────────────────────┘
               │
               │ WebSocket communication
               │
┌──────────────▼──────────────────────────────────────────┐
│                   TARGET CHATBOT                         │
│  (Your target system at ws://localhost:8001)             │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Attack Initiation

```
Frontend Form → POST /api/attack/start → Backend
                                          ├─ Save architecture file
                                          ├─ Update attack state
                                          ├─ Broadcast "attack_started"
                                          └─ Start async attack task
```

### 2. Real-Time Updates (WebSocket)

```
Attack Progress → WebSocket Broadcast → All Connected Frontends
                                        ├─ category_started
                                        ├─ turn_completed (future)
                                        ├─ category_completed
                                        └─ campaign_completed
```

### 3. Results Storage

```
Each Run → JSON File → attack_results/
                       ├─ standard_attack_run_1.json
                       ├─ standard_attack_run_2.json
                       ├─ standard_attack_run_3.json
                       ├─ crescendo_attack_run_1.json
                       └─ ...
```

## Features

### ✅ Implemented

1. **FastAPI Backend**
   - RESTful API endpoints
   - WebSocket support for real-time updates
   - File upload handling (architecture .md files)
   - Attack orchestration
   - Result storage and retrieval

2. **Web Frontend**
   - Modern, responsive UI
   - Real-time WebSocket connection
   - Attack configuration form
   - Category tabs for 4 attack types
   - Run cards showing 3 runs per category
   - Connection status indicator
   - Progress monitoring

3. **Real-Time Communication**
   - WebSocket connection management
   - Automatic reconnection on disconnect
   - Heartbeat/ping-pong mechanism
   - Broadcast messages to all clients

### 🎯 Category & Run Identification

The frontend clearly differentiates:

- **4 Category Tabs**: Standard, Crescendo, Skeleton Key, Obfuscation
- **3 Run Cards per Category**: Run 1, Run 2, Run 3
- **Visual States**:
  - Inactive: Gray/transparent
  - Active: Green glow (currently running)
  - Completed: Blue (finished successfully)

### 📊 Data Display

Each run card shows:
- Run number (1, 2, 3)
- Total turns executed
- Vulnerabilities found
- Visual state (active/completed)

## Usage Example

### 1. Start Backend

```bash
cd C:\RedTeaming\BACKEND
python api_server.py
```

Output:
```
    ╔════════════════════════════════════════════════════════════════════╗
    ║                                                                    ║
    ║   RED TEAM ATTACK ORCHESTRATOR - FastAPI Backend                  ║
    ║                                                                    ║
    ║   Real-time WebSocket Monitoring                                   ║
    ║   RESTful API for Attack Control                                   ║
    ║                                                                    ║
    ╚════════════════════════════════════════════════════════════════════╝

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### 2. Open Frontend

Open `C:\RedTeaming\FRONTEND\index.html` in your browser.

### 3. Configure & Launch

1. **WebSocket URL**: `ws://localhost:8001`
2. **Architecture File**: Upload your `AZURE_AGENT_ARCHITECTURE.md`
3. Click **🚀 Start Attack Campaign**

### 4. Monitor Progress

- Watch real-time updates in the UI
- Category tabs highlight current attack type
- Run cards update with statistics
- Turn log shows detailed information

## Testing

### Test WebSocket Connection

```python
import websockets
import asyncio
import json

async def test_ws():
    uri = "ws://localhost:8080/ws/attack-monitor"
    async with websockets.connect(uri) as websocket:
        # Wait for connection established
        msg = await websocket.recv()
        print(f"Received: {msg}")
        
        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))
        
        # Receive pong
        msg = await websocket.recv()
        print(f"Received: {msg}")

asyncio.run(test_ws())
```

### Test REST API

```bash
# Health check
curl http://localhost:8080/

# Get status
curl http://localhost:8080/api/status

# Get all results
curl http://localhost:8080/api/results

# Get specific run
curl http://localhost:8080/api/results/standard/1
```

## Troubleshooting

### Backend won't start

```bash
# Check if port 8080 is already in use
netstat -ano | findstr :8080

# Install dependencies
pip install fastapi uvicorn python-multipart websockets
```

### WebSocket not connecting

1. Check backend is running on port 8080
2. Check browser console for errors
3. Verify no firewall blocking WebSocket connections
4. Try changing WebSocket URL in frontend JavaScript

### File upload issues

1. Ensure file is .md or .txt format
2. Check file size (backend has no explicit limit but server may)
3. Verify `uploads/` directory exists (created automatically)

## Security Notes

⚠️ **Development Setup**: Current configuration allows all CORS origins (`allow_origins=["*"]`)

For production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Next Steps

To extend functionality:

1. **Turn-by-turn updates**: Modify orchestrators to broadcast each turn
2. **Detailed turn logs**: Display attack prompts and responses in frontend
3. **Export results**: Add download button for JSON results
4. **Attack history**: Store and display previous campaigns
5. **Authentication**: Add user authentication for multi-user environments
6. **Rate limiting**: Prevent API abuse
7. **Result analysis**: Add automated vulnerability analysis dashboard

---

**Created**: December 11, 2025  
**Backend**: FastAPI + WebSockets  
**Frontend**: Vanilla HTML/CSS/JavaScript  
**Communication**: REST API + WebSocket
