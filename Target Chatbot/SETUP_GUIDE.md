# Setup and Installation Guide for Target Chatbot

## System Requirements

- **Operating System**: Windows 10+ (or Linux/macOS with similar tools)
- **Python**: 3.8 or higher
- **Node.js**: 14.0 or higher  
- **npm**: 6.0 or higher

## Installation Steps

### Step 1: Verify Prerequisites

**Check Python:**
```powershell
python --version
# Should show Python 3.8 or higher
```

**Check Node.js and npm:**
```powershell
node --version
npm --version
# Should show v14 or higher for both
```

### Step 2: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

**Common Issues:**
- If pip fails, try: `python -m pip install --upgrade pip`
- Create virtual environment first:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### Step 3: Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

**Common Issues:**
- If npm is slow, try: `npm install --legacy-peer-deps`
- Clear cache: `npm cache clean --force`

### Step 4: Configure Backend

Edit `backend/chatbot_info.json` to configure:

```json
{
  "websocket_url": "ws://localhost:8001/ws",
  "domain": "E-Commerce",
  "chatbot_role": "E-Commerce Shopping Assistant"
}
```

### Step 5: Set Azure OpenAI Credentials

The backend needs Azure OpenAI API credentials. Set them in your environment or in `backend/config/settings.py`.

**Option A: Environment Variables**
```powershell
$env:AZURE_OPENAI_API_KEY="your-api-key"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
$env:AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

**Option B: Edit settings.py**
```python
AZURE_OPENAI_API_KEY = "your-api-key"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"
AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
```

## Running the System

### Option 1: Automated Startup (Recommended)

From the Target Chatbot root directory:

```powershell
.\start.ps1
```

This will:
1. Start the backend WebSocket server
2. Start the frontend development server  
3. Open the UI in your browser

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```powershell
.\start-backend.ps1
# Or manually:
cd backend
python chat_agent.py --port 8001
```

**Terminal 2 - Frontend:**
```powershell
.\start-frontend.ps1
# Or manually:
cd frontend
npm run dev
```

### Access Points

- **Frontend UI**: http://localhost:5173
- **Backend WebSocket**: ws://localhost:8001/ws

## Verification

### Backend Verification

1. Backend should show:
   ```
   Starting Azure OpenAI E-Commerce Agent...
   WebSocket server running on ws://0.0.0.0:8001
   Listening for connections...
   ```

2. Test connection:
   ```powershell
   # From PowerShell, test WebSocket connection
   $ws = New-Object Net.WebSockets.ClientWebSocket
   $ct = New-Object System.Threading.CancellationToken
   $ws.ConnectAsync("ws://localhost:8001/ws", $ct).Wait()
   Write-Host "Connected: $($ws.State)"
   ```

### Frontend Verification

1. Frontend should show:
   ```
   VITE v5.0.0  ready in XXX ms

   ➜  Local:   http://localhost:5173/
   ```

2. Open http://localhost:5173 in browser
3. Check for:
   - Green connection indicator (🟢 Connected)
   - Chat interface visible
   - Image upload button (🖼️) present

## Building for Production

### Frontend Build

```powershell
cd frontend
npm run build
```

Output will be in `frontend/dist/` directory.

Deploy this folder to your web server.

### Backend Deployment

For production use:
1. Use a WSGI server (e.g., Gunicorn, uWSGI)
2. Use SSL/TLS (WSS instead of WS)
3. Add authentication
4. Configure proper logging
5. Use environment variables for sensitive data

## Troubleshooting

### Issue: Backend won't start

**Solution:**
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt

# Run with verbose output
cd backend
python -u chat_agent.py --port 8001 --verbose
```

### Issue: Frontend can't connect to backend

**Check:**
1. Backend is running: `netstat -an | findstr 8001`
2. Correct WebSocket URL in `frontend/app.jsx`
3. Network firewall allows port 8001
4. Browser console for errors (F12)

**Fix:**
```powershell
# Update WebSocket URL in app.jsx
# Change: ws://localhost:8001/ws
# To: ws://<backend-ip>:8001/ws
```

### Issue: npm install fails

**Solutions:**
```powershell
# Clear npm cache
npm cache clean --force

# Install with legacy peer deps
npm install --legacy-peer-deps

# Use specific npm version
npm install -g npm@latest
npm install
```

### Issue: Python version compatibility

**Solution:**
```powershell
# Check Python version
python --version

# Use python3 if available
python3 -m pip install -r backend/requirements.txt
```

## Performance Optimization

### Frontend
- Use production build: `npm run build`
- Enable compression in web server
- Use CDN for static assets

### Backend
- Monitor memory usage for conversation history
- Implement message pagination
- Use caching for frequent queries
- Set connection timeouts

## Security Checklist

- [ ] Set strong Azure OpenAI API key
- [ ] Use environment variables for secrets
- [ ] Enable CORS restrictions if needed
- [ ] Add rate limiting on backend
- [ ] Use WSS (WebSocket Secure) for HTTPS
- [ ] Validate all user input on backend
- [ ] Sanitize chat messages
- [ ] Implement authentication if needed

## Next Steps

1. **First Use**: Send a test message to verify connectivity
2. **Upload Images**: Test image upload with the 🖼️ button
3. **Check Logs**: Review console output for any warnings
4. **Explore Features**: Try different types of queries
5. **Test Red-Team Prompts**: See vulnerabilities in action

## Getting Help

- **Frontend Issues**: Check browser console (F12)
- **Backend Issues**: Check terminal output
- **Connection Issues**: Verify ports 8001 and 5173 are open
- **Image Upload**: Check browser image size limits

## Additional Resources

- [Frontend README](frontend/README.md)
- [Backend Documentation](backend/CHATBOT_PROFILE_TEMPLATE.md)
- [Main README](README.md)

---

**Installation Complete!** 🎉

You're ready to use the Target Chatbot system.
