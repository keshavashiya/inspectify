#!/bin/bash
# Inspectify - Local Development Mode (Uvicorn)
# Quick start script for Linux/Mac

echo "🚀 Starting Inspectify in Local Development Mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check model file
if [ ! -f "models/yolo11m_trained.pt" ]; then
    echo "❌ Model file not found at models/yolo11m_trained.pt"
    echo "Please add your trained model file before running."
    exit 1
fi

# Set environment variables
export MODEL_PATH="models/yolo11m_trained.pt"
export ENV="development"
export SAVE_ANNOTATED_IMAGES="true"
export IMAGE_RETENTION_HOURS="24"
export OUTPUT_DIR="outputs/inspections"
export MAX_STORAGE_GB="10"

# Create output directories
mkdir -p outputs/inspections
mkdir -p logs

echo "✅ Starting Uvicorn server..."
echo "📍 Access at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
