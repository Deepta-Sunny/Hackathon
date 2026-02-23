# Start Air India Ai.g Middleware Server
# This server bridges api_server.py with the Ai.g chatbot on airindia.com

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Air India Ai.g Middleware Server Launcher   " -ForegroundColor Cyan
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
    Write-Host "⚠️ Warning: Activate script not found. Attempting to use python from venv directly." -ForegroundColor Yellow
}

if ($LASTEXITCODE -eq 0 -or $?) {
    Write-Host "Virtual environment activated!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "Make sure you have run: python -m venv venv" -ForegroundColor Red
    exit 1
}

# ── Configuration ──────────────────────────────────────────────────────────
$SERVER_HOST = "localhost"
$PORT        = 8002          # Ai.g middleware uses 8002 (Tia uses 8001)
$HEADLESS    = $false        # Set to $true for headless mode (no browser window)
# ───────────────────────────────────────────────────────────────────────────

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Target URL : https://www.airindia.com/" -ForegroundColor White
Write-Host "  WebSocket  : ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor White
Write-Host "  Headless   : $HEADLESS" -ForegroundColor White
Write-Host ""

Write-Host "Starting Air India Ai.g middleware server..." -ForegroundColor Yellow
Write-Host "This will:" -ForegroundColor White
Write-Host "  1. Open the Air India website" -ForegroundColor White
Write-Host "  2. Dismiss cookie consent popup (if present)" -ForegroundColor White
Write-Host "  3. Click the Ai.g chatbot icon (id='ask-aig')" -ForegroundColor White
Write-Host "  4. Verify chat input field (id='inputChat') is visible" -ForegroundColor White
Write-Host "  5. Start WebSocket server on ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor White
Write-Host "  6. Wait for api_server.py connections" -ForegroundColor White
Write-Host ""

Write-Host "➡️  Point api_server.py to: ws://${SERVER_HOST}:${PORT}/chat" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Build command
$cmd = "python aig_chatbot_automation.py --host $SERVER_HOST --port $PORT"
if ($HEADLESS) {
    $cmd += " --headless"
}

# Start server
Invoke-Expression $cmd
