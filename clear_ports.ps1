# PowerShell script to clear common ports used in the Red Teaming project
$TargetPorts = @(3000, 8000, 8001, 8005, 8080)

Write-Host "🧹 Clearing ports: $($TargetPorts -join ', ')..." -ForegroundColor Cyan

foreach ($Port in $TargetPorts) {
    # Get processes using the specific port
    $Connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($Connections) {
        $ProcessIds = $Connections.OwningProcess | Select-Object -Unique
        foreach ($CurrentPID in $ProcessIds) {
            $Process = Get-Process -Id $CurrentPID -ErrorAction SilentlyContinue
            if ($Process) {
                Write-Host "🛑 Stopping $($Process.ProcessName) (PID: $CurrentPID) on Port $Port" -ForegroundColor Yellow
                Stop-Process -Id $CurrentPID -Force
            }
        }
    } else {
        Write-Host "✅ Port $Port is already free." -ForegroundColor Green
    }
}

Write-Host "`n✨ All targeted ports have been cleared." -ForegroundColor Green
