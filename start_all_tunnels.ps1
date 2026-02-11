# Start both Ngrok tunnels (Backend & Frontend)

Write-Host "Starting Ngrok for both services..." -ForegroundColor Green
Write-Host "Backend: 8001 (Random Domain)"
Write-Host "Frontend: 3001 (Static Domain)"

ngrok start --all --config=ngrok_multi.yml

# Keep window open if it crashes immediately
Read-Host "Press Enter to exit"
