# Launch Ngrok Tunnels in new windows

Write-Host "Launching Ngrok tunnels..." -ForegroundColor Green

# Backend
Start-Process -FilePath "ngrok" -ArgumentList "http 8000"
Write-Host "Backend tunnel launched."

# Frontend
Start-Process -FilePath "ngrok" -ArgumentList "http 3000"
Write-Host "Frontend tunnel launched."

Write-Host ""
Write-Host "Please check the two new windows for your HTTPS URLs." -ForegroundColor Yellow
Write-Host "Copy the Backend URL to your app/frontend/.env.local file."
Write-Host "The Frontend URL is the one you share with others."
