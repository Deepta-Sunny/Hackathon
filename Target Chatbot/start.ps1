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

# Start backend as a background job in the current terminal
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    python chat_agent.py --port 8001
} -ArgumentList $backendPath

Write-Host "   Backend job started (Job ID: $($backendJob.Id))" -ForegroundColor Gray
Write-Host ""

# Wait for backend to start
Write-Host "Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show any backend output so far
$backendOutput = Receive-Job -Job $backendJob
if ($backendOutput) {
    Write-Host "--- Backend output ---" -ForegroundColor DarkGray
    $backendOutput | ForEach-Object { Write-Host "  [backend] $_" -ForegroundColor DarkGray }
    Write-Host "----------------------" -ForegroundColor DarkGray
    Write-Host ""
}

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
Write-Host "Stopping backend job..." -ForegroundColor Yellow
Stop-Job -Job $backendJob
Remove-Job -Job $backendJob
Write-Host "Backend stopped." -ForegroundColor Green
