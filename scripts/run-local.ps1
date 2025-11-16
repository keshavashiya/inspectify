# Inspectify - Local Development Mode (Uvicorn)
# Quick start script for Windows PowerShell

Write-Host "🚀 Starting Inspectify in Local Development Mode..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Check model file
if (-not (Test-Path "models/yolo11m_trained.pt")) {
    Write-Host "❌ Model file not found at models/yolo11m_trained.pt" -ForegroundColor Red
    Write-Host "Please add your trained model file before running." -ForegroundColor Red
    exit 1
}

# Set environment variables
$env:MODEL_PATH = "models/yolo11m_trained.pt"
$env:ENV = "development"
$env:SAVE_ANNOTATED_IMAGES = "true"
$env:IMAGE_RETENTION_HOURS = "24"
$env:OUTPUT_DIR = "outputs/inspections"
$env:MAX_STORAGE_GB = "10"

# Create output directories
New-Item -ItemType Directory -Force -Path "outputs/inspections" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "✅ Starting Uvicorn server..." -ForegroundColor Green
Write-Host "📍 Access at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
