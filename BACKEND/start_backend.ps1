# Start Backend Server Script
# Run this from the BACKEND directory

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                    ║" -ForegroundColor Cyan
Write-Host "║   RED TEAM ATTACK ORCHESTRATOR - Backend Startup                  ║" -ForegroundColor Cyan
Write-Host "║                                                                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the correct directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "📂 Working Directory: $scriptDir" -ForegroundColor Green
Write-Host "🐍 Using Python: .\venv\Scripts\python.exe" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Starting FastAPI backend on http://localhost:8080..." -ForegroundColor Yellow
Write-Host "🌐 WebSocket endpoint: ws://localhost:8080/ws/attack-monitor" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the server
.\venv\Scripts\python.exe api_server.py