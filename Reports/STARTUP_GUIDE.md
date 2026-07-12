# Red Team Testing System - Complete Startup Guide

## ⚠️ IMPORTANT: Required Services

The red-team testing system requires **3 separate services** to be running:

1. **Backend API Server** (Port 8080) - Attack orchestration
2. **Target Chat Agent** (Port 8001) - E-commerce chatbot being tested
3. **Frontend Dashboard** (Port 5173/5174) - User interface

---

## 🚀 Startup Sequence

### Step 1: Start the Target Chat Agent (MUST START FIRST)

**Terminal 1 (PowerShell):**
```powershell
cd "Target Chatbot\backend"
.\start_chat_agent.ps1
```

**Or manually:**
```powershell
cd BACKEND
.\venv\Scripts\Activate.ps1
cd "Target Chatbot/backend"
python chat_agent.py --port 8001
```

**Expected Output:**
```
🤖 Azure OpenAI E-Commerce Agent initialized
   📡 Listening on port 8001
   🔗 Target WebSocket: ws://localhost:8000/ws
   🔑 Using deployment: <your-deployment>
🚀 Starting Gemini E-Commerce Agent...
✅ WebSocket server started on ws://localhost:8001
```

**⚠️ CRITICAL:** Do NOT proceed until you see "WebSocket server started"

---

### Step 2: Start the Backend API Server

**Terminal 2 (PowerShell):**
```powershell
cd BACKEND
.\venv\Scripts\Activate.ps1
python api_server.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════════╗
║   RED TEAM ATTACK ORCHESTRATOR - FastAPI Backend                  ║
╚════════════════════════════════════════════════════════════════════╝

INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

---

### Step 3: Start the Frontend Dashboard

**Terminal 3 (PowerShell or Command Prompt):**
```powershell
cd FRONTEND\testeragent
npm run dev
```

**Expected Output:**
```
VITE ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## 🔍 Verification Checklist

Before starting an attack, verify all services are running:

### ✅ Chat Agent (Port 8001)
```powershell
# In any terminal:
curl ws://localhost:8001/ws
# Should NOT return "connection refused"
```

### ✅ Backend API (Port 8080)
Open browser: http://localhost:8080/docs
- Should show FastAPI Swagger documentation

### ✅ Frontend (Port 5173)
Open browser: http://localhost:5173/
- Should show Profile Setup form

---

## 🎯 Running an Attack

1. **Fill Profile Form** at http://localhost:5173/
   - Use the template from `Target Chatbot/backend/CHATBOT_PROFILE_TEMPLATE.md`
   - Ensure WebSocket URL is: `ws://localhost:8001/ws`

2. **Navigate to Dashboard** (automatic after form submission)

3. **Click "Start Testing"**
   - Backend terminal should show: "🚀 STARTING ATTACK CAMPAIGN EXECUTION"
   - Chat agent terminal should show incoming connections
   - Frontend should display real-time progress

---

## ❌ Troubleshooting

### Problem: "Connection Error: Unable to establish WebSocket connection"

**Cause:** Chat agent is not running on port 8001

**Solution:**
1. Check if chat agent is running (Terminal 1)
2. Verify output shows "✅ WebSocket server started on ws://localhost:8001"
3. If not running, start it using Step 1 above

---

### Problem: "Attack not starting" or "No communication"

**Checklist:**
1. ✅ Is chat_agent.py running? (Should be Terminal 1)
2. ✅ Is api_server.py running? (Should be Terminal 2)
3. ✅ Is frontend running? (Should be Terminal 3)
4. ✅ Did you use the correct WebSocket URL? (`ws://localhost:8001/ws`)

**Debugging:**
- Check Backend terminal for errors starting with "❌ ATTACK CAMPAIGN ERROR"
- Check Chat Agent terminal for connection attempts
- Check browser console for WebSocket errors

---

### Problem: Backend shows "Error sending personal message: Object not JSON serializable"

**Solution:** This is already fixed. Restart backend:
```powershell
# In Terminal 2:
Ctrl+C
python api_server.py
```

---

### Problem: Port already in use (8001, 8080, or 5173)

**Solution:**
```powershell
# Find process using port:
netstat -ano | findstr :8001
netstat -ano | findstr :8080
netstat -ano | findstr :5173

# Kill process by PID:
taskkill /PID <PID> /F

# Then restart the service
```

---

## 📊 Expected Terminal Activity During Attack

### Backend Terminal (api_server.py):
```
🚀 STARTING ATTACK CAMPAIGN EXECUTION
================================================================================
WebSocket URL: ws://localhost:8001/ws
Username: E-Commerce Shopping Assistant
Profile provided: True
================================================================================

[Category Started] Standard Attack
[Turn 1/30] Sending probe...
[Turn 2/30] Sending probe...
...
```

### Chat Agent Terminal (chat_agent.py):
```
📥 Received message: {"type": "query", "message": "...", "thread_id": "..."}
🤖 Processing query: ...
📤 Sending response: ...
📥 Received message: {"type": "query", "message": "...", "thread_id": "..."}
...
```

### Frontend Browser Console:
```
WebSocket connected
Category started: Standard Attack
Turn completed: 1/30
Turn completed: 2/30
...
```

---

## 🛑 Shutdown Sequence

1. **Stop Frontend** (Terminal 3): `Ctrl+C`
2. **Stop Backend** (Terminal 2): `Ctrl+C`
3. **Stop Chat Agent** (Terminal 1): `Ctrl+C`

---

## 📝 Quick Reference

| Service | Port | Command | Location |
|---------|------|---------|----------|
| Chat Agent | 8001 | `python chat_agent.py --port 8001` | `Target Chatbot/backend/` |
| Backend API | 8080 | `python api_server.py` | `BACKEND/` |
| Frontend | 5173 | `npm run dev` | `FRONTEND/testeragent/` |

---

## ✅ Full Working Example

**Terminal 1:**
```powershell
PS C:\Hackathon\RedTeaming\BACKEND> .\venv\Scripts\Activate.ps1
(venv) PS C:\Hackathon\RedTeaming> cd "Target Chatbot\backend"
(venv) PS C:\Hackathon\RedTeaming\Target Chatbot\backend> python chat_agent.py
🤖 Azure OpenAI E-Commerce Agent initialized
✅ WebSocket server started on ws://localhost:8001
```

**Terminal 2:**
```powershell
PS C:\Hackathon\RedTeaming\BACKEND> .\venv\Scripts\Activate.ps1
(venv) PS C:\Hackathon\RedTeaming\BACKEND> python api_server.py
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

**Terminal 3:**
```powershell
PS C:\Hackathon\RedTeaming\FRONTEND\testeragent> npm run dev
➜  Local:   http://localhost:5173/
```

**Browser:** Navigate to http://localhost:5173/ and start testing!

---

**Last Updated:** January 28, 2026
