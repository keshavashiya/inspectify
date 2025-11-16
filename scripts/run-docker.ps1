# Inspectify - Docker Compose Mode
# Quick start script for Windows PowerShell

Write-Host "🐳 Starting Inspectify with Docker Compose..." -ForegroundColor Cyan

# Check if Docker is running
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check model file
if (-not (Test-Path "models/yolo11m_trained.pt")) {
    Write-Host "❌ Model file not found at models/yolo11m_trained.pt" -ForegroundColor Red
    Write-Host "Please add your trained model file before running." -ForegroundColor Red
    exit 1
}

Write-Host "🔨 Building and starting containers..." -ForegroundColor Yellow
docker-compose up --build

Write-Host ""
Write-Host "✅ Service started!" -ForegroundColor Green
Write-Host "📍 Access at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
