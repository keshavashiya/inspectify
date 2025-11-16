# Inspectify Quick Start Scripts

These scripts help you quickly start Inspectify in different modes.

## Usage

### Windows PowerShell

```powershell
# Mode 1: Local Development (Uvicorn)
.\scripts\run-local.ps1

# Mode 2: Docker Compose
.\scripts\run-docker.ps1

# Mode 3: Kubernetes (Minikube)
.\scripts\run-k8s.ps1
```

### Linux/Mac (Bash)

```bash
# Mode 1: Local Development (Uvicorn)
./scripts/run-local.sh

# Mode 2: Docker Compose
./scripts/run-docker.sh

# Mode 3: Kubernetes (Minikube)
./scripts/run-k8s.sh
```

## What Each Script Does

### run-local (.ps1/.sh)
- Creates virtual environment if needed
- Installs Python dependencies
- Sets environment variables
- Starts Uvicorn with hot reload
- Creates output directories

### run-docker (.ps1/.sh)
- Checks if Docker is running
- Verifies model file exists
- Builds and starts containers with docker-compose
- Shows access URLs

### run-k8s (.ps1/.sh)
- Checks kubectl and minikube installation
- Starts Minikube if not running
- Switches to Minikube's Docker daemon
- Builds image in Minikube
- Deploys all Kubernetes resources
- Sets up port forwarding
- Shows useful kubectl commands

## Prerequisites

### All Modes
- Trained model file at `models/yolo11m_trained.pt`

### Local Mode
- Python 3.11+
- pip

### Docker Mode
- Docker Desktop

### Kubernetes Mode
- Docker Desktop
- kubectl
- Minikube

## Stopping Services

```powershell
# Local: Press Ctrl+C in terminal

# Docker: 
docker-compose down

# Kubernetes:
kubectl delete -f k8s/
minikube stop
```
