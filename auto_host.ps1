# Auto Host Script
# Starts Backend (Local) -> Updates Frontend Config -> Builds/Starts Frontend -> Ngrok Frontend (Static Domain)

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
    # Increased timeout to 60 seconds (30 * 2s)
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

# Cleanup function
function Cleanup-Services {
    Write-Host "Stopping services..."
    if ($global:backendProcess) { Stop-Process -Id $global:backendProcess.Id -ErrorAction SilentlyContinue }
    if ($global:frontendProcess) { Stop-Process -Id $global:frontendProcess.Id -ErrorAction SilentlyContinue }
    if ($global:ngrokFrontendProcess) { Stop-Process -Id $global:ngrokFrontendProcess.Id -ErrorAction SilentlyContinue }
    
    # Force kill just in case
    Stop-Process -Name "ngrok" -ErrorAction SilentlyContinue
    Stop-Process -Name "uvicorn" -ErrorAction SilentlyContinue
    # Stop-Process -Name "node" -ErrorAction SilentlyContinue # Be careful with node
    
    Write-Host "Services stopped."
}

# 1. Start Backend
Write-Host "Starting Backend..." -ForegroundColor Cyan
# Force host 127.0.0.1
$global:backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -PassThru -WindowStyle Minimized
Write-Host "Backend started (PID: $($global:backendProcess.Id))." -ForegroundColor Green

Wait-ForPort -Port 8000

# 2. Update Frontend Config
Write-Host "Updating Frontend Configuration..." -ForegroundColor Cyan
$envFile = "app/frontend/.env.local"
# Set to empty string to use relative paths (handled by Next.js rewrites)
$envContent = "NEXT_PUBLIC_API_URL="
Set-Content -Path $envFile -Value $envContent
Write-Host "Updated $envFile" -ForegroundColor Green

# 3. Build Frontend
Write-Host "Building Frontend (this may take a while)..." -ForegroundColor Cyan
Push-Location "app/frontend"
try {
    # npm install # Skip install to save time, assume installed
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
}
catch {
    Pop-Location
    Cleanup-Services
    throw "Frontend build failed: $_"
}
finally {
    Pop-Location
}

# 4. Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Push-Location "app/frontend"
# Force hostname to 127.0.0.1 to avoid IPv6 ambiguity
$global:frontendProcess = Start-Process -FilePath "npm" -ArgumentList "start -- -H 127.0.0.1 -p 3000" -PassThru -WindowStyle Minimized
Pop-Location
Write-Host "Frontend started (PID: $($global:frontendProcess.Id))." -ForegroundColor Green

Wait-ForPort -Port 3000

# 5. Start Frontend Ngrok
Write-Host "Starting Ngrok for Frontend (Port 3000)..." -ForegroundColor Cyan

# Create temp config for frontend ngrok
# Explicitly use 127.0.0.1:3000
$ngrokFrontendConfig = @"
version: 2
authtoken: 36KX1H8tq6wpA3rKAvuYUvSFOHS_52LcvTZ1RQvCcBx2CLosP
web_addr: localhost:4040
tunnels:
  frontend_static:
    proto: http
    addr: 127.0.0.1:3000
    hostname: uncausative-cenogenetically-valene.ngrok-free.dev
"@
Set-Content -Path "ngrok_frontend_static.yml" -Value $ngrokFrontendConfig

$global:ngrokFrontendProcess = Start-Process -FilePath "ngrok" -ArgumentList "start --config=ngrok_frontend_static.yml frontend_static" -PassThru -WindowStyle Minimized
Write-Host "Ngrok Frontend started (PID: $($global:ngrokFrontendProcess.Id))." -ForegroundColor Green

# Wait for Ngrok to initialize
Write-Host "Waiting for Ngrok Frontend URL..."
Start-Sleep -Seconds 5

$frontendUrl = $null
for ($i = 0; $i -lt 10; $i++) {
    $frontendUrl = Get-NgrokUrl -ApiUrl "http://localhost:4040"
    if ($frontendUrl) { break }
    Start-Sleep -Seconds 2
}

if (-not $frontendUrl) {
    Cleanup-Services
    throw "Failed to get Frontend Ngrok URL."
}

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "Hosting Setup Complete!" -ForegroundColor Green
Write-Host "Application URL: $frontendUrl" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Press any key to stop all services..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Cleanup-Services
