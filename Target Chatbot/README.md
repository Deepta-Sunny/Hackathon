# Target Chatbot - Complete System Setup Guide

## Quick Start

### Option 1: Start Everything Together (Recommended)

```powershell
.\start.ps1
```

This script will:
1. Start the backend WebSocket server on port 8001
2. Install frontend dependencies if needed
3. Start the frontend development server on port 5173
4. Open both endpoints in your browser

### Option 2: Start Frontend and Backend Separately

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
```

### Option 3: Manual Setup

**Backend:**
```powershell
cd backend
python chat_agent.py --port 8001
```

**Frontend:**
```powershell
cd frontend
npm install  # First time only
npm run dev
```

## Directory Structure

```
Target Chatbot/
├── backend/                      # Backend WebSocket server
│   ├── chat_agent.py            # Main chatbot agent
│   ├── ecommerce_db_schema.py   # Database schema
│   ├── chatbot_info.json        # Configuration
│   ├── vulnerable_prompts.txt   # Test prompts
│   ├── requirements.txt         # Python dependencies
│   ├── chat_memory.db           # Chat history
│   └── start_chat_agent.ps1     # Legacy startup script
│
├── frontend/                     # React-based UI
│   ├── app.jsx                  # Main React component
│   ├── index.html               # HTML entry point
│   ├── styles.css               # UI styling
│   ├── websocket-service.js     # WebSocket client
│   ├── image-handler.js         # Image upload handler
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js           # Vite configuration
│   └── README.md                # Frontend documentation
│
├── start.ps1                     # Start all services
├── start-backend.ps1            # Start backend only
├── start-frontend.ps1           # Start frontend only
└── README.md                     # This file
```

## Features

### Backend
- ✅ WebSocket server on ws://localhost:8001/ws
- ✅ Azure OpenAI integration
- ✅ E-commerce database simulation
- ✅ Conversation memory management
- ✅ Red-team attack vector support

### Frontend
- ✅ Modern React UI
- ✅ Image upload (drag & drop)
- ✅ Real-time chat via WebSocket
- ✅ Connection status indicator
- ✅ Auto-reconnection
- ✅ Responsive design

## Endpoints

- **Backend WebSocket**: `ws://localhost:8001/ws`
- **Frontend UI**: `http://localhost:5173`

## Configuration

### Backend Configuration

Edit [backend/chatbot_info.json](backend/chatbot_info.json):

```json
{
  "websocket_url": "ws://localhost:8001/ws",
  "domain": "E-Commerce",
  "chatbot_role": "E-Commerce Shopping Assistant"
}
```

### Frontend Configuration

Edit [frontend/app.jsx](frontend/app.jsx) to change WebSocket URL:

```javascript
wsRef.current = new WebSocketService('ws://your-server:port/ws');
```

## Prerequisites

### For Backend
- Python 3.8 or later
- Azure OpenAI API key
- Dependencies in `backend/requirements.txt`

### For Frontend
- Node.js 14 or later
- npm or yarn

## Installation Steps

### First Time Setup

1. **Backend Dependencies:**
   ```powershell
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

2. **Frontend Dependencies:**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

3. **Configure Backend:**
   - Set Azure OpenAI credentials in `backend/config/settings.py`
   - Update `backend/chatbot_info.json` if needed

### Running

```powershell
.\start.ps1
```

Or start services individually:

```powershell
.\start-backend.ps1   # Terminal 1
.\start-frontend.ps1  # Terminal 2
```

## Usage

1. **Open Frontend**: Navigate to http://localhost:5173
2. **Send Messages**: Type in the chat box and press Enter
3. **Upload Images**: 
   - Click 🖼️ button to select images
   - Or drag & drop images onto the chat window
4. **View Status**: Check the connection indicator in the header

## Image Upload

### Supported Formats
- JPEG
- PNG
- GIF
- WebP

### Limits
- Maximum file size: 5MB per image
- Maximum dimensions: 4096x4096 px

## Troubleshooting

### Backend won't start

1. Try configuring python environment:
   ```powershell
   cd BACKEND
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Correct path:
   ```powershell
   # From repo root
   cd Target Chatbot/backend
   python chat_agent.py --port 8001
   ```

3. Check logs:
   ```powershell
   tail -f BACKEND/logs/app.log
   ```

### Frontend won't connect

1. Check backend is running on port 8001
2. Verify WebSocket URL in `frontend/app.jsx`
3. Check browser console for errors
4. Update CORS if backend on different server

### Images not uploading

1. Check file size (max 5MB)
2. Verify file format (JPEG, PNG, GIF, WebP)
3. Check browser console for detailed errors

### Connection drops frequently

1. Check network stability
2. Increase reconnection timeout in `frontend/websocket-service.js`
3. Check backend logs for errors

## Advanced Usage

### Running on Different Machines

**Backend Machine (e.g., 192.168.1.100):**
```powershell
.\start-backend.ps1
```

**Frontend Machine:**
1. Edit `frontend/app.jsx`:
   ```javascript
   wsRef.current = new WebSocketService('ws://192.168.1.100:8001/ws');
   ```

2. Start frontend:
   ```powershell
   npm run dev -- --host 0.0.0.0
   ```

### Production Deployment

**Build Frontend:**
```powershell
cd frontend
npm run build
```

Deploy `frontend/dist/` to your web server.

**Run Backend:**
- Use process manager (PM2, systemd, etc.)
- Configure proper logging
- Set environment variables for Azure OpenAI

## Environment Variables

### Backend
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: Model deployment name
- `AZURE_OPENAI_API_VERSION`: API version (e.g., 2024-02-15-preview)

### Frontend
- `VITE_BACKEND_URL`: Backend WebSocket URL (for build-time config)

## Performance Tips

1. **Frontend:**
   - Use production build for deployment
   - Clear chat history periodically for long sessions
   - Compress images before upload

2. **Backend:**
   - Monitor conversation memory usage
   - Implement rate limiting for testing
   - Use caching for frequent queries

## Security Considerations

⚠️ **For Testing Only:**
- No authentication enabled by default
- CORS not restricted
- All data stored in memory
- Images stored in messages

For production, implement:
- Authentication/authorization
- CORS restrictions
- Rate limiting
- Input validation
- Secure WebSocket (WSS)
- Data persistence with encryption

## For Red Team Testing

This system is designed as a vulnerable target for security testing:

1. **Attack Vectors**: See [backend/vulnerable_prompts.txt](backend/vulnerable_prompts.txt)
2. **Test Patterns**: Review [BACKEND/attack_strategies/](../BACKEND/attack_strategies/)
3. **Documentation**: Check [backend/CHATBOT_PROFILE_TEMPLATE.md](backend/CHATBOT_PROFILE_TEMPLATE.md)

## Support & Logs

- **Frontend logs**: Browser console (F12)
- **Backend logs**: Terminal output or `BACKEND/logs/`
- **Chat history**: `backend/chat_memory.db`
- **Documentation**: See individual README.md files

## License

Part of the Target Chatbot suite for Red Team Testing.

---

**Last Updated**: March 21, 2026
**Version**: 1.0.0
