# Master Startup Script for Red Teaming Environment
# 1. CLEAR PORTS FIRST
Write-Host "Clearing all project ports (3000, 8000, 8001, 8005, 8080)..." -ForegroundColor Cyan
.\clear_ports.ps1

Write-Host "`nSTARTING RED TEAMING SYSTEM...`n" -ForegroundColor Green

# 2. PATHS
$VenvPath = "$PWD\BACKEND\venv\Scripts\Activate.ps1"
$ChatbotPath = "$PWD\Target Chatbot"
$MiddlewarePath = "$PWD\BACKEND\middlewares"

# 3. Start Target Chatbot (In a new terminal)
Write-Host "Starting Target Chatbot in new window..." -ForegroundColor Yellow
$ChatbotCmd = "Set-Location '$ChatbotPath'; . '$VenvPath'; .\start.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $ChatbotCmd -WindowStyle Normal

Write-Host "Waiting for UI to initialize (15s)..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# 4. Start Selenium Middleware (In a new terminal)
Write-Host "Starting Selenium Middleware in new window..." -ForegroundColor Yellow
$MiddlewareCmd = "Set-Location '$MiddlewarePath'; . '$VenvPath'; python -u custom_chatbot_middleware.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $MiddlewareCmd -WindowStyle Normal

Write-Host "Waiting for Selenium browser and middleware (10s)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# 5. Running Automation Test (In the current terminal)
Write-Host "RUNNING AUTOMATION TEST..." -ForegroundColor Red
Set-Location "$ChatbotPath"
. "$VenvPath"
python .\test_iamge_based_jailbreaking.py

Write-Host "`nAutomation Run Complete." -ForegroundColor Green
Write-Host "Review the outputs and close the windows when done." -ForegroundColor Gray
