# Start Target Chatbot UI Middleware Server
# This server bridges api_server.py with the Target Chatbot frontend UI.

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Target Chatbot UI Middleware Launcher" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the correct directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Activate script not found. Attempting to use python from venv directly." -ForegroundColor Yellow
}

if ($LASTEXITCODE -eq 0 -or $?) {
    Write-Host "Virtual environment activated!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "Make sure you have run: python -m venv venv" -ForegroundColor Red
    exit 1
}

# Configuration
$TARGET_UI_URL = "http://localhost:3000"
$SERVER_HOST   = "localhost"
$PORT          = 8002
$HEADLESS      = $false

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Target UI : $TARGET_UI_URL" -ForegroundColor White
Write-Host "  WebSocket : ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor White
Write-Host "  Headless  : $HEADLESS" -ForegroundColor White
Write-Host ""

Write-Host "Starting Target Chatbot UI middleware server..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  1. Open Target Chatbot frontend UI" -ForegroundColor White
Write-Host "  2. Use id='chat-textarea' to type messages" -ForegroundColor White
Write-Host "  3. Use id='send-button' to submit" -ForegroundColor White
Write-Host "  4. Read assistant responses from id='bot-bubble-*'" -ForegroundColor White
Write-Host "  5. Start WebSocket server on ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor White
Write-Host ""

Write-Host "Point api_server.py to: ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Build command
$cmd = "python middlewares/target_chatbot_ui_middleware.py --url `"$TARGET_UI_URL`" --host $SERVER_HOST --port $PORT"
if ($HEADLESS) {
    $cmd += " --headless"
}

# Start server
Invoke-Expression $cmd
