# Inspectify - Kubernetes Mode (Minikube)
# Quick start script for Windows PowerShell

Write-Host "☸️  Starting Inspectify with Kubernetes..." -ForegroundColor Cyan

# Check if kubectl is installed
$kubectlInstalled = Get-Command kubectl -ErrorAction SilentlyContinue
if (-not $kubectlInstalled) {
    Write-Host "❌ kubectl not found. Install from: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Red
    exit 1
}

# Check if minikube is installed
$minikubeInstalled = Get-Command minikube -ErrorAction SilentlyContinue
if (-not $minikubeInstalled) {
    Write-Host "❌ minikube not found. Install from: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Red
    exit 1
}

# Check model file
if (-not (Test-Path "models/yolo11m_trained.pt")) {
    Write-Host "❌ Model file not found at models/yolo11m_trained.pt" -ForegroundColor Red
    Write-Host "Please add your trained model file before running." -ForegroundColor Red
    exit 1
}

# Start Minikube if not running
Write-Host "🔧 Checking Minikube status..." -ForegroundColor Yellow
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🚀 Starting Minikube..." -ForegroundColor Yellow
    minikube start --driver=docker
}

# Switch to Minikube's Docker daemon
Write-Host "🐳 Switching to Minikube's Docker daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build image
Write-Host "🔨 Building Docker image in Minikube..." -ForegroundColor Yellow
docker build -t inspectify:latest .

# Deploy to Kubernetes
Write-Host "☸️  Deploying to Kubernetes..." -ForegroundColor Yellow
kubectl apply -f k8s/

# Wait for pods to be ready
Write-Host "⏳ Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=inspectify,component=api --timeout=120s

# Start port forwarding in background
Write-Host "🔌 Setting up port forwarding..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward service/inspectify-api 8000:80"

Write-Host ""
Write-Host "✅ Kubernetes deployment complete!" -ForegroundColor Green
Write-Host "📍 Access at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  kubectl get pods              # View pod status" -ForegroundColor Gray
Write-Host "  kubectl logs -f deployment/inspectify-api  # View logs" -ForegroundColor Gray
Write-Host "  kubectl delete -f k8s/        # Stop and remove" -ForegroundColor Gray
Write-Host "  minikube stop                 # Stop Minikube" -ForegroundColor Gray
