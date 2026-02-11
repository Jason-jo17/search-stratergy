# Helper to update Backend URL and restart Frontend

$url = Read-Host "Please paste the Backend Ngrok URL (from the other window)"

if ([string]::IsNullOrWhiteSpace($url)) {
    Write-Error "You didn't paste a URL!"
    exit 1
}

# Update .env.local
$content = "NEXT_PUBLIC_API_URL=$url"
Set-Content -Path "app/frontend/.env.local" -Value $content
Write-Host "Updated configuration to use: $url" -ForegroundColor Green

# Restart Frontend
Write-Host "Restarting Frontend..." -ForegroundColor Cyan
Stop-Process -Name "node" -ErrorAction SilentlyContinue
Start-Process -FilePath "npm" -ArgumentList "run dev -- -p 3001" -WorkingDirectory "app/frontend" -WindowStyle Minimized
Write-Host "Frontend restarted! You can now open the Frontend Ngrok URL." -ForegroundColor Green

Read-Host "Press Enter to exit"
