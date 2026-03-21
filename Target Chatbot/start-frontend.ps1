# Start only the Frontend for Target Chatbot
# Use this if backend is running separately or on a remote server

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  Target Chatbot - Frontend Only" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the Target Chatbot root directory" -ForegroundColor Red
    exit 1
}

Write-Host "📦 Starting Frontend Development Server..." -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  ✅ Frontend Starting!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend UI: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚙️  Configuration:" -ForegroundColor Yellow
Write-Host "   Backend WebSocket: ws://localhost:8001/ws" -ForegroundColor Gray
Write-Host ""
Write-Host "   💡 Update the WebSocket URL in app.jsx if backend is on different host" -ForegroundColor Cyan
Write-Host ""

npm run dev
