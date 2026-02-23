# Web Chatbot Middleware Integration Guide

## Overview

The Web Chatbot Middleware bridges the gap between `api_server.py` (which expects WebSocket-based chatbots) and web-based chatbots (like Tia on Air India Express).

## Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐         Selenium         ┌─────────────────┐
│                 │    (ws://localhost:8001)    │                  │    (Browser Automation)  │                 │
│  api_server.py  │ ───────────────────────────>│    Middleware    │ ───────────────────────> │  Air India Tia  │
│                 │                             │     Server       │                          │    Chatbot      │
│  (Orchestrator) │ <───────────────────────────│                  │ <─────────────────────── │   (Web-based)   │
│                 │         Responses           │                  │       Responses          │                 │
└─────────────────┘                             └──────────────────┘                          └─────────────────┘
```

### Components

1. **api_server.py**: The main red teaming orchestration system
   - Uses `ChatbotWebSocketTarget` to connect to chatbots
   - Expects WebSocket protocol with JSON messages
   - Unchanged - just point to middleware WebSocket URL

2. **web_chatbot_middleware.py**: The bridge server
   - Provides WebSocket server interface
   - Maintains `WebScreenTarget` (Selenium browser)
   - Translates between WebSocket protocol and web automation
   - Keeps the web chatbot open throughout the session

3. **WebScreenTarget** (in `core/web_screen_target.py`): Web automation
   - Uses Selenium to interact with web chatbots
   - Finds and clicks chatbot buttons
   - Sends messages and extracts responses

## Setup & Installation

### 1. Install Dependencies

```powershell
# Already installed in your venv:
# - websockets
# - selenium
# - webdriver-manager
```

### 2. Start the Middleware Server

**Option A: Using PowerShell Script (Recommended)**

```powershell
cd BACKEND
.\start_airindiaexpress_middleware.ps1
```

**Option B: Manual Command**

```powershell
cd BACKEND
.\venv\Scripts\Activate.ps1
python web_chatbot_middleware.py --url "https://www.airindiaexpress.com/" --port 8001
```

**Options:**
- `--url`: Target web chatbot URL (default: Air India Express)
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8001)
- `--headless`: Run browser in headless mode (no window)

### 3. Verify Middleware is Running

You should see:
```
================================================================================
🌐 INITIALIZING WEB CHATBOT CONNECTION
================================================================================
Target URL: https://www.airindiaexpress.com/
Headless: False
================================================================================

🔗 Connecting to web chatbot...
[WebScreen-Selenium] Initializing Chrome Driver...
[WebScreen-Selenium] Navigating to https://www.airindiaexpress.com/...
[WebScreen-Selenium] Found chatbot button with: //*[contains(translate...
[WebScreen-Selenium] Clicked chatbot button, waiting for chat to open...
✅ Web chatbot connected and ready!

================================================================================
🚀 STARTING WEBSOCKET MIDDLEWARE SERVER
================================================================================
WebSocket URL: ws://localhost:8001/chat
Target: https://www.airindiaexpress.com/
Ready to accept connections from api_server.py
================================================================================

✅ [Middleware] Server running on ws://localhost:8001/chat
[Middleware] Waiting for connections...
```

## Usage

### Option 1: Use with api_server.py (Frontend Dashboard)

1. Start the middleware server (as shown above)
2. Start the frontend dashboard
3. In the dashboard, configure chatbot settings:
   - **WebSocket URL**: `ws://localhost:8001/chat`
   - Fill in other chatbot profile details
4. Click "Start Attack Campaign"

The `api_server.py` will connect to the middleware, which will forward messages to the Tia chatbot.

### Option 2: Direct API Call to api_server.py

```python
import requests

# Create chatbot profile
profile = {
    "username": "RedTeamTester",
    "websocket_url": "ws://localhost:8001/chat",  # <-- Middleware URL
    "domain": "Aviation/Airline Customer Service",
    "primary_objective": "Assist customers with flight services",
    "intended_audience": "Airline passengers",
    "chatbot_role": "Virtual assistant",
    "capabilities": ["Flight bookings", "Cancellations", "Refunds"],
    "boundaries": "Must maintain privacy and security",
    "communication_style": "Friendly and professional"
}

# Start attack campaign
response = requests.post(
    "http://localhost:8000/api/start-attack",
    json={
        "username": "RedTeamTester",
        "chatbot_profile": profile
    }
)
```

### Option 3: Standalone Script (for testing)

```python
from core.orchestrator import ThreeRunCrescendoOrchestrator

orchestrator = ThreeRunCrescendoOrchestrator(
    websocket_url="ws://localhost:8001/chat",  # <-- Middleware URL
    chatbot_profile=your_profile
)

report = await orchestrator.execute_full_assessment()
```

## Testing the Middleware

### Basic Test

```powershell
# Terminal 1: Start middleware
.\start_airindiaexpress_middleware.ps1

# Terminal 2: Run test
python test_airindiaexpress_middleware.py
```

The test script will:
1. Connect to middleware
2. Send 3 test messages
3. Verify responses are received
4. Test ping/pong health check

## Protocol Details

### Message Format (api_server.py → Middleware)

```json
{
    "type": "query",
    "message": "Can you help me with flight cancellation?",
    "thread_id": "uuid-here"
}
```

### Response Format (Middleware → api_server.py)

```json
{
    "type": "response",
    "message": "Hey there! I can help you with flight cancellations...",
    "timestamp": "2026-02-16T23:45:00",
    "thread_id": "uuid-here"
}
```

### Special Messages

**Reset Conversation:**
```json
{
    "type": "reset",
    "thread_id": "uuid-here"
}
```

**Health Check:**
```json
{
    "type": "ping"
}
```

**Response:**
```json
{
    "type": "pong",
    "message": "Middleware is alive",
    "timestamp": "2026-02-16T23:45:00"
}
```

## Standard Attack with Middleware

Here's the complete workflow:

```powershell
# Step 1: Start Middleware (keeps Tia chatbot open)
cd BACKEND
.\start_airindiaexpress_middleware.ps1

# Step 2: In another terminal, start attacker
cd BACKEND
.\venv\Scripts\Activate.ps1
python

# In Python:
import asyncio
from api_server import execute_attack_campaign
from models.chatbot_profile import ChatbotProfile

profile = ChatbotProfile(
    username="RedTeamTester",
    websocket_url="ws://localhost:8001/chat",  # <-- Middleware!
    domain="Aviation/Airline Customer Service",
    primary_objective="Assist customers with flights",
    intended_audience="Airline passengers",
    chatbot_role="Virtual assistant",
    capabilities=["Bookings", "Cancellations"],
    boundaries="Privacy and security",
    communication_style="Friendly"
)

# Run standard attack only
asyncio.run(execute_attack_campaign(
    websocket_url="ws://localhost:8001/chat",
    chatbot_profile=profile
))
```

## Troubleshooting

### Middleware won't start
- Check if port 8001 is already in use
- Verify Selenium and webdriver-manager are installed
- Check Chrome/Chromium is installed

### Can't find chatbot button
- The middleware looks for "need help" or "chat with tia" text
- If the website changes, update selectors in `web_screen_target.py`

### Responses are empty
- Check browser console for JavaScript errors
- Website might have changed its structure
- Check `web_screen_target.py` response extraction logic

### Connection refused from api_server.py
- Ensure middleware is running first
- Check firewall isn't blocking localhost:8001
- Verify WebSocket URL is correct: `ws://localhost:8001/chat`

## Benefits of Middleware Architecture

1. **No Changes to api_server.py**: The orchestration system remains unchanged
2. **Reusable**: Can be adapted for other web-based chatbots
3. **Debugging**: Browser window is visible (when not headless)
4. **Session Persistence**: Chatbot stays open for entire attack campaign
5. **Protocol Compatibility**: Translates between WebSocket and web automation

## Files Created

- `BACKEND/web_chatbot_middleware.py` - Main middleware server
- `BACKEND/start_airindiaexpress_middleware.ps1` - Startup script
- `BACKEND/test_airindiaexpress_middleware.py` - Test client
- `BACKEND/MIDDLEWARE_GUIDE.md` - This documentation
- `BACKEND/core/web_screen_target.py` - Web automation (already existed, enhanced)

## Next Steps

1. Start middleware server
2. Test with `test_airindiaexpress_middleware.py`
3. Run standard attack through api_server.py
4. Monitor both terminals for progress
5. Retrieve attack reports from `attack_results/` folder
