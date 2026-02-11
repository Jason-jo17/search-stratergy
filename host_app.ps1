# Optimized Hosting Script
# Usage: .\host_app.ps1

$ErrorActionPreference = "Stop"

function Get-NgrokUrl {
    param (
        [string]$ApiUrl
    )
    try {
        $tunnels = Invoke-RestMethod -Uri "$ApiUrl/api/tunnels" -ErrorAction Stop
        if ($tunnels.tunnels.Count -gt 0) {
            return $tunnels.tunnels[0].public_url
        }
    }
    catch {
        Write-Host "Waiting for ngrok API at $ApiUrl..."
    }
    return $null
}

function Wait-ForPort {
    param (
        [int]$Port
    )
    Write-Host "Waiting for port $Port to be active..."
    for ($i = 0; $i -lt 30; $i++) {
        $conn = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
        if ($conn.TcpTestSucceeded) {
            Write-Host "Port $Port is active." -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "Timeout waiting for port $Port."
}

# 1. Start Backend
Write-Host "1. Starting Backend..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -PassThru -WindowStyle Minimized
Write-Host "Backend started (PID: $($backendProcess.Id))." -ForegroundColor Green

Wait-ForPort -Port 8000

# 2. Update Frontend Config
Write-Host "2. Updating Frontend Configuration..." -ForegroundColor Cyan
$envFile = "app/frontend/.env.local"
$envContent = "NEXT_PUBLIC_API_URL=" # Empty for relative paths
Set-Content -Path $envFile -Value $envContent
Write-Host "Updated $envFile" -ForegroundColor Green

# 3. Start Frontend (In New Window)
Write-Host "3. Starting Frontend (New Window)..." -ForegroundColor Cyan
$frontendCmd = "cd app/frontend; npm start -- -H 127.0.0.1 -p 3000"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "$frontendCmd" -WindowStyle Normal
Write-Host "Frontend launched in new window." -ForegroundColor Green

# 4. Start Ngrok
Write-Host "4. Starting Ngrok..." -ForegroundColor Cyan
$ngrokConfig = @"
version: 2
authtoken: 36KX1H8tq6wpA3rKAvuYUvSFOHS_52LcvTZ1RQvCcBx2CLosP
web_addr: localhost:4040
tunnels:
  frontend_static:
    proto: http
    addr: 127.0.0.1:3000
    hostname: uncausative-cenogenetically-valene.ngrok-free.dev
"@
Set-Content -Path "ngrok_host.yml" -Value $ngrokConfig

$ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList "start --config=ngrok_host.yml frontend_static" -PassThru -WindowStyle Minimized
Write-Host "Ngrok started (PID: $($ngrokProcess.Id))." -ForegroundColor Green

# 5. Get URL
Write-Host "Waiting for Ngrok URL..."
Start-Sleep -Seconds 5
$url = $null
for ($i = 0; $i -lt 10; $i++) {
    $url = Get-NgrokUrl -ApiUrl "http://localhost:4040"
    if ($url) { break }
    Start-Sleep -Seconds 2
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "   HOSTING ACTIVE" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Public URL: $url" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Keep this window open to monitor status."
Write-Host "To stop: Close this window and the Frontend window."
