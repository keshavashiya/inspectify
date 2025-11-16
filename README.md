# Inspectify

AI-powered vehicle damage detection and inspection system using YOLO11m with automated image annotation and storage.

## Overview

Inspectify is a production-ready FastAPI service that automatically detects and classifies vehicle damage using deep learning. The system processes images via URL or file upload, applies intelligent enhancement for low-light conditions, and returns detailed damage assessments with annotated images showing bounding boxes around detected damage.

## Deployment Modes

```ini
┌─────────────────────────────────────────────────────────────────┐
│                    Choose Your Deployment Mode                  │
└─────────────────────────────────────────────────────────────────┘

Mode 1: Uvicorn (Local)          Mode 2: Docker Compose          Mode 3: Kubernetes
┌──────────────────┐             ┌──────────────────┐            ┌──────────────────┐
│   Your Machine   │             │  Docker Engine   │            │    Minikube      │
│  ┌────────────┐  │             │  ┌────────────┐  │            │  ┌────────────┐  │
│  │  Python    │  │             │  │ Container  │  │            │  │   Pod 1    │  │
│  │  Uvicorn   │  │             │  │ Inspectify │  │            │  │ Inspectify │  │
│  │  FastAPI   │  │             │  │   API      │  │            │  └────────────┘  │
│  └────────────┘  │             │  └────────────┘  │            │  ┌────────────┐  │
│   Port: 8000     │             │   Port: 8000     │            │  │   Pod 2    │  │
└──────────────────┘             └──────────────────┘            │  │ Inspectify │  │
                                                                 │  └────────────┘  │
✅ Fast startup                  ✅ Isolated                    │  ┌────────────┐  │
✅ Hot reload                    ✅ Production-like             │  │   Redis    │  │
❌ No isolation                  ❌ Single instance             │  └────────────┘  │
                                                                 │   Port: 8000     │
                                                                 └──────────────────┘
                                                                  ✅ Auto-scaling
                                                                  ✅ Self-healing
                                                                  ✅ Load balancing

```

## Key Features

- � **6 Damaege Types**: Detects dents, scratches, cracks, broken lamps, shattered glass, and flat tires
- 🤖 **YOLO11m Model**: State-of-the-art object detection with configurable confidence thresholds
- 📸 **Smart Enhancement**: Automatic low-light image enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
- 💾 **Dual Storage**: In-memory caching for fast retrieval + disk storage for annotated images
- 🖼️ **Image Annotation**: Automatically saves original and annotated versions with bounding boxes
- 📊 **Damage Metrics**: Severity assessment, pixel area calculations, and detailed detection statistics
- 🔄 **Auto Cleanup**: Configurable retention period with automatic expiration (default 24 hours)
- 🐳 **Docker Ready**: Fully containerized with health checks and volume management
- 🔧 **Configurable**: Environment-based configuration for all major settings

## Quick Start

Choose your deployment mode based on your needs:

### Mode 1: Local Development (Uvicorn) ⚡

**Best for**: Quick testing, development, debugging

```bash
# Prerequisites
# - Python 3.11+
# - Trained model at models/yolo11m_trained.pt

# Setup
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000

```

**Pros**: Fast startup, hot reload, easy debugging  
**Cons**: No isolation, manual dependency management

---

### Mode 2: Docker Compose 🐳

**Best for**: Testing containerization, simple deployments

```bash
# Prerequisites
# - Docker Desktop installed
# - Model at models/yolo11m_trained.pt

# Run
docker-compose up --build

# Access at http://localhost:8000
# Wait 30-40 seconds for model loading

```

**Pros**: Isolated environment, production-like setup  
**Cons**: Slower startup than uvicorn

---

### Mode 3: Kubernetes (Minikube) ☸️

**Best for**: Learning K8s, production-ready orchestration, scaling

```bash
# Prerequisites
# - Docker Desktop
# - kubectl installed
# - Minikube installed

# Setup
minikube start --driver=docker

# Build image in Minikube
minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker build -t inspectify:latest .

# Deploy
kubectl apply -f k8s/

# Access
kubectl port-forward service/inspectify-api 8000:80
# Access at http://localhost:8000

# See k8s/README.md for detailed instructions

```

**Pros**: Auto-scaling, self-healing, load balancing, production-ready  
**Cons**: More complex setup, resource intensive

---

### Quick Comparison

| Feature | Uvicorn | Docker Compose | Kubernetes |
|---------|---------|----------------|------------|
| Startup Time | ~5s | ~30s | ~60s |
| Auto-scaling | ❌ | ❌ | ✅ |
| Self-healing | ❌ | ✅ (restart) | ✅ (full) |
| Load Balancing | ❌ | ❌ | ✅ |
| Resource Limits | ❌ | ✅ | ✅ |
| Hot Reload | ✅ | ❌ | ❌ |
| Complexity | Low | Medium | High |

---

### Quick Start Scripts

For even faster setup, use the provided scripts:

**Windows PowerShell:**

```powershell
.\scripts\run-local.ps1    # Mode 1: Uvicorn
.\scripts\run-docker.ps1   # Mode 2: Docker
.\scripts\run-k8s.ps1      # Mode 3: Kubernetes

```

**Linux/Mac:**

```bash
./scripts/run-local.sh     # Mode 1: Uvicorn
./scripts/run-docker.sh    # Mode 2: Docker
./scripts/run-k8s.sh       # Mode 3: Kubernetes

```

See `scripts/README.md` for details.

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "model_loaded": true,
#   "image_storage_enabled": true,
#   "cache_stats": {...},
#   "storage_stats": {...}
# }

```

### First Detection

```bash
# Upload an image for inspection
curl -X POST http://localhost:8000/detect/upload \
  -F "file=@your_car_image.jpg" \
  -F "vehicle_id=TEST001"

# Download the annotated image (use inspection_id from response)
curl "http://localhost:8000/results/{inspection_id}/image" -o annotated.jpg

```

## API Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/health

```

### 2. Detect from URL

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/car.jpg",
    "vehicle_id": "ABC123",
    "confidence_threshold": 0.5,
    "enable_enhancement": true
  }'

```

### 3. Detect from File Upload

```bash
curl -X POST http://localhost:8000/detect/upload \
  -F "file=@car_image.jpg" \
  -F "vehicle_id=ABC123" \
  -F "confidence_threshold=0.5" \
  -F "enable_enhancement=true"

```

### 4. Get Inspection Results

```bash
curl http://localhost:8000/results/{inspection_id}

```

### 5. Get Annotated Image

```bash
# Get annotated image with bounding boxes
curl http://localhost:8000/results/{inspection_id}/image?image_type=annotated -o annotated.jpg

# Get original image
curl http://localhost:8000/results/{inspection_id}/image?image_type=original -o original.jpg

```

### 6. Get Image Metadata

```bash
curl http://localhost:8000/results/{inspection_id}/metadata

```

### 7. Delete Inspection

```bash
curl -X DELETE http://localhost:8000/results/{inspection_id}

```

### 8. Cache Statistics

```bash
curl http://localhost:8000/cache/stats

```

### 9. Manual Cleanup

```bash
curl -X POST http://localhost:8000/cache/cleanup

```

## Configuration

Environment variables (set in `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SAVE_ANNOTATED_IMAGES` | `true` | Enable/disable image storage |
| `IMAGE_RETENTION_HOURS` | `24` | How long to keep images |
| `OUTPUT_DIR` | `outputs/inspections` | Where to store images |
| `MAX_STORAGE_GB` | `10` | Maximum disk space for images |

## Response Format

```json
{
  "status": "success",
  "inspection_id": "uuid-here",
  "vehicle_id": "ABC123",
  "timestamp": "2025-11-16T10:30:00",
  "damage_metrics": {
    "total_detections": 3,
    "dents": 1,
    "scratches": 2,
    "severity": "moderate",
    "total_damage_pixels": 15000
  },
  "detections": [
    {
      "class_name": "dent",
      "confidence": 0.85,
      "bbox": {
        "x_min": 100,
        "y_min": 200,
        "x_max": 300,
        "y_max": 400,
        "width": 200,
        "height": 200
      },
      "pixel_area": 40000
    }
  ],
  "processing_time_ms": 250.5,
  "image_enhanced": false,
  "message": "Detection complete: 3 damage(s) found"
}

```

## Storage Structure

```ini
outputs/
└── inspections/
    └── {inspection_id}/
        ├── original.jpg      # Original uploaded image
        ├── annotated.jpg     # Image with bounding boxes
        └── metadata.json     # Detection metadata

```

## Project Structure

```ini
inspectify/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── detection.py         # YOLO11m detector implementation
│   ├── image_processor.py   # Image download, validation, resizing
│   ├── image_storage.py     # Disk storage for annotated images
│   ├── retinex.py          # Low-light enhancement (CLAHE)
│   ├── cache.py            # In-memory caching layer
│   ├── config.py           # Configuration management
│   └── models.py           # Pydantic data models
├── models/
│   └── yolo11m_trained.pt  # Trained YOLO11m weights
├── outputs/                 # Auto-created for image storage
│   └── inspections/
│       └── {inspection_id}/
│           ├── original.jpg
│           ├── annotated.jpg
│           └── metadata.json
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── ARCHITECTURE.md        # System architecture details

```

## Development

### Testing All Modes

```bash
# Mode 1: Uvicorn (fastest for development)
uvicorn app.main:app --reload

# Mode 2: Docker Compose (test containerization)
docker-compose up --build

# Mode 3: Kubernetes (test orchestration)
kubectl port-forward service/inspectify-api 8000:80

```

### Running Tests

```bash
# Test health endpoint (works for all modes)
curl http://localhost:8000/health

# Test detection with sample image
curl -X POST http://localhost:8000/detect/upload \
  -F "file=@test_images/sample_car.jpg" \
  -F "vehicle_id=DEV001"

```

### Switching Between Modes

```bash
# Stop Docker Compose
docker-compose down

# Stop Kubernetes
kubectl delete -f k8s/
minikube stop

# Stop Uvicorn
# Ctrl+C in terminal

```

## Technical Details

### Image Processing Pipeline

1. **Input Validation**: Size check (max 50MB), format validation
2. **Preprocessing**: Resize to max 1280px width, maintain aspect ratio
3. **Enhancement**: Auto-detect low-light (brightness < 90), apply CLAHE if needed
4. **Detection**: YOLO11m inference with configurable confidence threshold
5. **Post-processing**: Calculate metrics, generate annotated image
6. **Storage**: Save to cache (JSON) and disk (images)

### Damage Classification

- **Dent**: Body panel deformations
- **Scratch**: Surface paint damage
- **Crack**: Structural cracks in body/glass
- **Broken Lamp**: Damaged headlights/taillights
- **Shattered Glass**: Broken windows/windshield
- **Flat Tire**: Deflated or damaged tires

### Severity Levels

- **None**: No damage detected
- **Minor**: < 5,000 pixels total damage area
- **Moderate**: 5,000 - 20,000 pixels
- **Severe**: > 20,000 pixels

## Performance & Limits

- **Detection Speed**: 200-500ms per image (CPU), 50-150ms (GPU)
- **Max Image Size**: 50MB
- **Image Retention**: 24 hours (configurable)
- **Max Storage**: 10GB (configurable)
- **Concurrent Requests**: Thread-safe, no hard limit
- **Cache Expiration**: 24 hours
- **Auto Cleanup**: Runs on manual trigger or scheduled

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs -f api

# Verify model file
docker-compose exec api ls -la /app/models/

# Check port availability
netstat -an | grep 8000

```

### Model not loading

- Ensure `models/yolo11m_trained.pt` exists and is valid
- Check file permissions
- Verify sufficient RAM (minimum 4GB)

### Out of disk space

```bash
# Check storage stats
curl http://localhost:8000/health | jq '.storage_stats'

# Manual cleanup
curl -X POST http://localhost:8000/cache/cleanup

# Reduce retention period in docker-compose.yml
IMAGE_RETENTION_HOURS: "12"

```

### Slow performance

- Enable GPU support in Docker (if available)
- Reduce image sizes before upload
- Increase confidence threshold to reduce false positives
- Consider horizontal scaling with load balancer

## Future Enhancements

Potential improvements for production deployment:

- Authentication & API key management
- Rate limiting per client
- Webhook notifications for async processing
- Database integration for persistent storage
- Multi-model ensemble for improved accuracy
- Real-time video stream processing
- Mobile SDK for direct integration
- Admin dashboard for monitoring
- Batch processing API
- Export to PDF reports

## License & Credits

- YOLO11m: Ultralytics (AGPL-3.0)
- FastAPI: Sebastián Ramírez (MIT)
- OpenCV: Intel Corporation (Apache 2.0)

## 📚 Documentation

- **[README.md](README.md)** - This file: Complete setup, API reference, and usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flow, and technical details
- **[k8s/README.md](k8s/README.md)** - Kubernetes deployment guide and commands
- **[scripts/README.md](scripts/README.md)** - Quick start scripts for all modes

## Support

For issues, questions, or contributions:

1. Check logs: `docker-compose logs -f api` or `kubectl logs -f deployment/inspectify-api`
2. Review ARCHITECTURE.md for system details
3. Verify configuration in docker-compose.yml or k8s/*.yaml
4. Ensure model file is present and valid at `models/yolo11m_trained.pt`
