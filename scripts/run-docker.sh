#!/bin/bash
# Inspectify - Docker Compose Mode
# Quick start script for Linux/Mac

echo "🐳 Starting Inspectify with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

# Check model file
if [ ! -f "models/yolo11m_trained.pt" ]; then
    echo "❌ Model file not found at models/yolo11m_trained.pt"
    echo "Please add your trained model file before running."
    exit 1
fi

echo "🔨 Building and starting containers..."
docker-compose up --build

echo ""
echo "✅ Service started!"
echo "📍 Access at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
