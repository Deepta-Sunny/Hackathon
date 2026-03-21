# Start only the Backend WebSocket Server
# Use this if frontend is running separately or on a different machine

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  Target Chatbot - Backend Only" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: backend directory not found" -ForegroundColor Red
    Write-Host "   Please run this script from the Target Chatbot root directory" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Starting Backend WebSocket Server..." -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Activate virtual environment if available
if (Test-Path "../../venv/Scripts/Activate.ps1") {
    Write-Host "🐍 Activating Python virtual environment..." -ForegroundColor Yellow
    & ../../venv/Scripts/Activate.ps1
} else {
    Write-Host "⚠️  Virtual environment not found, using system Python" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  ✅ Backend Starting!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🔌 WebSocket Endpoint: ws://localhost:8001/ws" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Port: 8001" -ForegroundColor Gray
Write-Host "   Protocol: WebSocket (ws://)" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Make sure Azure OpenAI credentials are configured in:" -ForegroundColor Yellow
Write-Host "   config/settings.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python chat_agent.py --port 8001