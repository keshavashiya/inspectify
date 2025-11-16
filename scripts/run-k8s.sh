#!/bin/bash
# Inspectify - Kubernetes Mode (Minikube)
# Quick start script for Linux/Mac

echo "☸️  Starting Inspectify with Kubernetes..."

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Install from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube not found. Install from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check model file
if [ ! -f "models/yolo11m_trained.pt" ]; then
    echo "❌ Model file not found at models/yolo11m_trained.pt"
    echo "Please add your trained model file before running."
    exit 1
fi

# Start Minikube if not running
echo "🔧 Checking Minikube status..."
if ! minikube status > /dev/null 2>&1; then
    echo "🚀 Starting Minikube..."
    minikube start --driver=docker
fi

# Switch to Minikube's Docker daemon
echo "🐳 Switching to Minikube's Docker daemon..."
eval $(minikube docker-env)

# Build image
echo "🔨 Building Docker image in Minikube..."
docker build -t inspectify:latest .

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
kubectl apply -f k8s/

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=inspectify,component=api --timeout=120s

# Start port forwarding in background
echo "🔌 Setting up port forwarding..."
kubectl port-forward service/inspectify-api 8000:80 > /dev/null 2>&1 &
PORT_FORWARD_PID=$!

echo ""
echo "✅ Kubernetes deployment complete!"
echo "📍 Access at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  kubectl get pods              # View pod status"
echo "  kubectl logs -f deployment/inspectify-api  # View logs"
echo "  kubectl delete -f k8s/        # Stop and remove"
echo "  minikube stop                 # Stop Minikube"
echo ""
echo "Port forwarding PID: $PORT_FORWARD_PID"
echo "To stop port forwarding: kill $PORT_FORWARD_PID"
