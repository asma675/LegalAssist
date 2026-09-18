$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path "backend\.env")) {
  Copy-Item "backend\.env.example" "backend\.env"
  Write-Host "Created backend\.env from example. Review SECRET_KEY before production." -ForegroundColor Yellow
}
Write-Host "Building and starting Rafi v2..." -ForegroundColor Cyan
docker compose up -d --build
Write-Host "" 
docker compose ps
Write-Host "" 
Write-Host "Rafi:      http://localhost:8080" -ForegroundColor Green
Write-Host "API docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health:    http://localhost:8080/api/health" -ForegroundColor Green
Write-Host "Login:     admin@rafi.app / ChangeMe123!" -ForegroundColor Yellow
