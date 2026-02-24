# Start the E-Commerce Chat Agent (Target for Red-Team Testing)
# This script activates the virtual environment and starts the chat agent WebSocket server

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  E-Commerce Chat Agent - Red Team Testing Target" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

# Navigate to parent directory to activate venv
Set-Location ..

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Navigate back to target chatbot directory
Set-Location "target chatbot"

# Start the chat agent
Write-Host ""
Write-Host "Starting E-Commerce Chat Agent on ws://localhost:8001..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the agent" -ForegroundColor Yellow
Write-Host ""

python chat_agent.py --port 8001
