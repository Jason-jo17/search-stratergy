# Setup and Run VectorPrompt Hosting

Write-Host "Starting setup..." -ForegroundColor Green

# 1. Install Ngrok if not present
if (!(Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Ngrok..." -ForegroundColor Cyan
    winget install Ngrok.Ngrok
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Winget install failed. Please install Ngrok manually from https://ngrok.com/download" -ForegroundColor Red
    }
    # Refresh env vars
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Ngrok is already installed." -ForegroundColor Green
}

# 2. Install Python Dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r app/requirements.txt

# 3. Install Node Dependencies
Write-Host "Installing Node dependencies..." -ForegroundColor Cyan
cd app/frontend
npm install

# 4. Build Frontend
Write-Host "Building Frontend..." -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed! Attempting to run in Development Mode instead..." -ForegroundColor Yellow
    $runDev = Read-Host "Do you want to run in Development Mode? (y/n)"
    if ($runDev -ne 'y') {
        exit 1
    }
    $frontendCmd = "npm run dev"
} else {
    $frontendCmd = "npm start"
}

# 5. Start Backend
Write-Host "Starting Backend..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WindowStyle Minimized
Write-Host "Backend started in background." -ForegroundColor Green

# 6. Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Cyan
# Split command for Start-Process if needed, but npm run dev/start is simple
if ($frontendCmd -eq "npm run dev") {
    Start-Process -FilePath "npm" -ArgumentList "run dev" -WindowStyle Minimized
} else {
    Start-Process -FilePath "npm" -ArgumentList "start" -WindowStyle Minimized
}
Write-Host "Frontend started in background." -ForegroundColor Green

# 7. Start Ngrok
Write-Host "Services are running!" -ForegroundColor Green
Write-Host "1. Backend: http://localhost:8000"
Write-Host "2. Frontend: http://localhost:3000"
Write-Host ""
Write-Host "To share with others, run these commands in separate terminals:" -ForegroundColor Yellow
Write-Host "ngrok http 8000"
Write-Host "ngrok http 3000"
Write-Host ""
Write-Host "Note: You need to update app/frontend/.env.local with the backend ngrok URL and rebuild (or restart dev server) if you want the frontend to talk to the backend via ngrok." -ForegroundColor Yellow

Read-Host -Prompt "Press Enter to exit"
