# Start the Frontend and Backend for Target Chatbot
# Run this script from the Target Chatbot directory

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  Target Chatbot - Full Stack Startup" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "ERROR: Please run this script from the Target Chatbot root directory" -ForegroundColor Red
    Write-Host "   This directory should contain 'backend' and 'frontend' folders" -ForegroundColor Red
    exit 1
}

$rootPath = (Get-Location).Path
Write-Host "Root path: $rootPath" -ForegroundColor Gray
Write-Host ""

# --- Start Backend in new window ---
$backendPath = Join-Path $rootPath "backend"
Write-Host "Starting Backend WebSocket Server..." -ForegroundColor Yellow
Write-Host "   Directory: $backendPath" -ForegroundColor Gray
Write-Host "   Endpoint:  ws://localhost:8001/ws" -ForegroundColor Cyan
Write-Host ""

# Start backend in a NEW WINDOW so logs are visible
$backendCmd = "Set-Location '$backendPath'; python -u chat_agent.py --port 8001; Read-Host 'Backend stopped. Press Enter to exit'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Write-Host "   Backend started in a new window" -ForegroundColor Gray
Write-Host ""

# Wait for backend to start
Write-Host "Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# --- Start Frontend ---
$frontendPath = Join-Path $rootPath "frontend"
Write-Host ""
Write-Host "Starting Frontend Development Server..." -ForegroundColor Yellow
Write-Host "   Directory: $frontendPath" -ForegroundColor Gray

Set-Location $frontendPath

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install frontend dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  System Starting!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend WebSocket : ws://localhost:8001/ws" -ForegroundColor Cyan
Write-Host "  Frontend UI       : http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop the frontend" -ForegroundColor Yellow
Write-Host "  Close the backend window to stop the backend" -ForegroundColor Yellow
Write-Host ""

npm run dev

# Cleanup backend job when frontend exits
Write-Host ""
Write-Host "Frontend stopped." -ForegroundColor Yellow
Write-Host "Please close the backend window manually." -ForegroundColor Gray
Write-Host "Backend stopped." -ForegroundColor Green
