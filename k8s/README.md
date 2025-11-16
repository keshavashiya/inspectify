# Kubernetes Setup Guide

## What is Kubernetes?
Kubernetes (K8s) is a container orchestration platform that automates deployment, scaling, and management of containerized applications.

## Key Concepts

### 1. **Pods**
- Smallest deployable unit in K8s
- Contains one or more containers
- Shares network and storage

### 2. **Deployments**
- Manages replica sets and pods
- Handles rolling updates and rollbacks
- Ensures desired number of pods are running

### 3. **Services**
- Provides stable networking for pods
- Load balances traffic across pods
- Types: ClusterIP, NodePort, LoadBalancer

### 4. **ConfigMaps**
- Stores configuration data
- Decouples config from container images

## Setup Instructions

### Prerequisites
```bash
# Install kubectl (Kubernetes CLI)
# Windows: choco install kubernetes-cli
# Or download from: https://kubernetes.io/docs/tasks/tools/

# Install Minikube (local K8s cluster)
# Windows: choco install minikube
# Or download from: https://minikube.sigs.k8s.io/docs/start/
```

### Step 1: Start Minikube
```bash
minikube start --driver=docker
```

### Step 2: Build Docker Image in Minikube
```bash
# Point Docker CLI to Minikube's Docker daemon
minikube docker-env
# Run the command it outputs, then:

docker build -t inspectify:latest .
```

### Step 3: Deploy to Kubernetes
```bash
# Apply all configurations
kubectl apply -f k8s/

# Or apply individually:
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 4: Check Status
```bash
# View all resources
kubectl get all

# View pods
kubectl get pods

# View services
kubectl get services

# View logs
kubectl logs -f deployment/inspectify-api
```

### Step 5: Access Application
```bash
# Option 1: Port Forwarding (Recommended for Windows)
kubectl port-forward service/inspectify-api 8000:80
# Access at: http://localhost:8000
# Keep this terminal open while using the service

# Option 2: Minikube Service Tunnel (Windows)
minikube service inspectify-api
# This opens browser automatically and creates a tunnel
# IMPORTANT: Keep the terminal open - closing it breaks the connection
```

## Useful Commands

### Monitoring
```bash
# Watch pod status
kubectl get pods -w

# Describe pod (detailed info)
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash
```

### Scaling
```bash
# Scale deployment
kubectl scale deployment inspectify-api --replicas=3

# Auto-scale based on CPU
kubectl autoscale deployment inspectify-api --min=2 --max=5 --cpu-percent=80
```

### Updates
```bash
# Update image
kubectl set image deployment/inspectify-api inspectify-api=inspectify:v2

# Check rollout status
kubectl rollout status deployment/inspectify-api

# Rollback
kubectl rollout undo deployment/inspectify-api
```

### Cleanup
```bash
# Delete all resources
kubectl delete -f k8s/

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## How K8s Tracks Your Docker Application

### 1. **Health Checks**
- **Liveness Probe**: Restarts container if unhealthy
- **Readiness Probe**: Removes pod from service if not ready

### 2. **Resource Management**
- **Requests**: Minimum resources guaranteed
- **Limits**: Maximum resources allowed
- K8s schedules pods based on available resources

### 3. **Self-Healing**
- Automatically restarts failed containers
- Replaces and reschedules pods on node failure
- Kills containers that don't respond to health checks

### 4. **Service Discovery**
- Services get DNS names (e.g., redis-service)
- Pods can communicate using service names
- Load balancing across healthy pods

### 5. **Monitoring**
```bash
# View resource usage
kubectl top pods
kubectl top nodes

# View events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Production Considerations

### 1. **Persistent Storage**
Add PersistentVolumeClaims for data that needs to survive pod restarts

### 2. **Secrets Management**
Use Kubernetes Secrets for sensitive data instead of ConfigMaps

### 3. **Ingress**
Use Ingress controller for advanced routing and SSL termination

### 4. **Namespaces**
Organize resources into namespaces for multi-environment setups

### 5. **Monitoring Stack**
- Prometheus for metrics
- Grafana for visualization
- ELK/EFK stack for logging

## Learning Resources
- Official Docs: https://kubernetes.io/docs/
- Interactive Tutorial: https://kubernetes.io/docs/tutorials/
- Minikube: https://minikube.sigs.k8s.io/
