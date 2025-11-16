# Inspectify - System Architecture

## Overview

Inspectify is a microservice-based vehicle damage detection system built on FastAPI, YOLO11m deep learning model, and a dual-storage architecture (in-memory cache + disk storage). The system is designed for high-throughput inspection workflows with automatic image annotation and configurable retention policies.

## Design Principles

- **Stateless API**: Each request is independent, enabling horizontal scaling
- **Dual Storage**: Fast in-memory cache for JSON + persistent disk storage for images
- **Automatic Cleanup**: Time-based expiration prevents storage overflow
- **Thread-Safe**: Concurrent request handling without race conditions
- **Configurable**: Environment-based configuration for all major settings
- **Docker-First**: Containerized deployment with health checks

## Component Diagram

```ini
┌─────────────────────────────────────────────────────────────┐
│                         Client                              │
│                    (HTTP Requests)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI App                            │
│                     (app/main.py)                           │
├─────────────────────────────────────────────────────────────┤
│  Endpoints:                                                 │
│  • POST /detect                                             │
│  • POST /detect/upload                                      │
│  • GET /results/{id}                                        │
│  • GET /results/{id}/image                                  │
│  • GET /results/{id}/metadata                               │
│  • DELETE /results/{id}                                     │
│  • GET /health                                              │
│  • GET /cache/stats                                         │
│  • POST /cache/cleanup                                      │
└──┬────────┬──────────┬──────────┬──────────┬────────────────┘
   │        │          │          │          │
   ▼        ▼          ▼          ▼          ▼
┌──────┐ ┌─────┐ ┌─────────┐ ┌──────┐ ┌────────────┐
│Image │ │YOLO │ │ Retinex │ │Cache │ │   Image    │
│Proc. │ │11m  │ │Enhancer │ │      │ │  Storage   │
└──────┘ └─────┘ └─────────┘ └──────┘ └────────────┘
   │        │          │          │          │
   │        │          │          │          ▼
   │        │          │          │    ┌──────────────┐
   │        │          │          │    │   outputs/   │
   │        │          │          │    │ inspections/ │
   │        │          │          │    │  {id}/       │
   │        │          │          │    │  - original  │
   │        │          │          │    │  - annotated │
   │        │          │          │    │  - metadata  │
   │        │          │          │    └──────────────┘
   │        │          │          ▼
   │        │          │    ┌──────────────┐
   │        │          │    │  In-Memory   │
   │        │          │    │    Cache     │
   │        │          │    │  (24 hours)  │
   │        │          │    └──────────────┘
   │        │          │
   │        ▼          ▼
   │   ┌──────────────────┐
   │   │  ML Processing   │
   │   │  - Detection     │
   │   │  - Enhancement   │
   │   └──────────────────┘
   │
   ▼
┌──────────────────┐
│  Image Sources   │
│  - URL Download  │
│  - File Upload   │
└──────────────────┘

```

## Request Flow

### Detection Request Flow

```ini
1. Client Request
   ├─ POST /detect (URL)
   └─ POST /detect/upload (File)
        │
        ▼
2. Image Acquisition
   ├─ Download from URL
   └─ Read uploaded file
        │
        ▼
3. Image Processing
   ├─ Validate size (< 50MB)
   ├─ Decode image
   ├─ Get metadata (brightness, dimensions)
   └─ Resize if needed (max 1280px)
        │
        ▼
4. Enhancement (if enabled)
   ├─ Check brightness < 90
   └─ Apply CLAHE if low-light
        │
        ▼
5. ML Detection
   ├─ YOLO11m inference
   ├─ Generate bounding boxes
   └─ Create annotated image
        │
        ▼
6. Calculate Metrics
   ├─ Count detections by type
   ├─ Calculate total damage pixels
   └─ Determine severity
        │
        ▼
7. Storage (Parallel)
   ├─ Cache results (in-memory)
   └─ Save images (disk)
        │
        ▼
8. Response
   └─ Return JSON with inspection_id

```

### Image Retrieval Flow

```ini
1. Client Request
   └─ GET /results/{id}/image?image_type=annotated
        │
        ▼
2. Check Storage Enabled
   ├─ If disabled → 503 Error
   └─ If enabled → Continue
        │
        ▼
3. Load Image
   ├─ Read from disk
   └─ If not found → 404 Error
        │
        ▼
4. Encode & Return
   ├─ Encode as JPEG
   └─ Return binary response

```

## Data Flow

```ini
┌──────────────┐
│ Image Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ ImageProcessor   │
│ - Download/Read  │
│ - Validate       │
│ - Resize         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ RetinexEnhancer  │
│ - Check light    │
│ - Apply CLAHE    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ YOLO11mDetector  │
│ - Inference      │
│ - Bounding boxes │
│ - Annotate       │
└──────┬───────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ InMemoryCache│  │ ImageStorage │
│ - JSON data  │  │ - Original   │
│ - 24h TTL    │  │ - Annotated  │
│              │  │ - Metadata   │
└──────────────┘  └──────────────┘

```

## Storage Architecture

### In-Memory Cache

```json
{
  "inspection_id": {
    "data": {
      "status": "success",
      "inspection_id": "uuid",
      "vehicle_id": "ABC123",
      "damage_metrics": {...},
      "detections": [...]
    },
    "created_at": "2025-11-16T10:30:00"
  }
}

```

### Disk Storage (NEW)

```ini
outputs/inspections/
├── {inspection_id_1}/
│   ├── original.jpg       (Original image)
│   ├── annotated.jpg      (With bounding boxes)
│   └── metadata.json      (Vehicle ID, timestamp, etc.)
├── {inspection_id_2}/
│   ├── original.jpg
│   ├── annotated.jpg
│   └── metadata.json
└── ...

```

## Component Details

### 1. ImageProcessor (app/image_processor.py)

- Downloads images from URLs
- Processes uploaded files
- Validates size (max 50MB)
- Extracts metadata (dimensions, brightness)
- Resizes images (max 1280px width)

### 2. RetinexEnhancer (app/retinex.py)

- Detects low-light conditions (brightness < 90)
- Applies CLAHE enhancement
- Improves detection accuracy in poor lighting

### 3. YOLO11mDetector (app/detection.py)

- Loads YOLO11m model
- Runs inference
- Generates bounding boxes
- Creates annotated images
- Calculates damage metrics

### 4. InMemoryCache (app/cache.py)

- Thread-safe storage
- 24-hour TTL
- Automatic expiration
- Statistics tracking

### 5. ImageStorage (app/image_storage.py)

- Saves original and annotated images
- Stores metadata as JSON
- Retrieves images by ID
- Automatic cleanup (24 hours)
- Disk usage monitoring
- Thread-safe operations

## Technology Stack

### Core Framework

- **FastAPI**: Modern async web framework with automatic OpenAPI docs
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### Machine Learning

- **Ultralytics YOLO11m**: Object detection model
- **PyTorch**: Deep learning framework
- **TorchVision**: Computer vision utilities
- **OpenCV**: Image processing and manipulation

### Storage & Caching

- **In-Memory Cache**: Thread-safe dictionary with TTL
- **File System**: Local disk storage for images
- **JSON**: Metadata serialization

### Infrastructure

- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Python 3.11**: Runtime environment

### Dependencies

```ini
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
opencv-python==4.8.1.78
numpy==1.26.2
ultralytics==8.0.200
torch==2.1.0
torchvision==0.16.0
requests==2.31.0
python-multipart==0.0.6
Pillow==10.1.0

```

## Configuration

### Environment Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `MODEL_PATH` | `models/yolo11m_trained.pt` | Path to YOLO model weights | Yes |
| `SAVE_ANNOTATED_IMAGES` | `true` | Enable disk storage for images | No |
| `IMAGE_RETENTION_HOURS` | `24` | How long to keep images (hours) | No |
| `OUTPUT_DIR` | `outputs/inspections` | Directory for image storage | No |
| `MAX_STORAGE_GB` | `10` | Maximum disk space for images (GB) | No |
| `ENV` | `testing` | Environment identifier | No |

### Configuration Examples

**Development (Fast iteration, no storage):**

```yaml
environment:
  SAVE_ANNOTATED_IMAGES: "false"
  IMAGE_RETENTION_HOURS: "1"
  MAX_STORAGE_GB: "1"

```

**Production (Full features, longer retention):**

```yaml
environment:
  SAVE_ANNOTATED_IMAGES: "true"
  IMAGE_RETENTION_HOURS: "168"  # 7 days
  OUTPUT_DIR: /mnt/shared/inspections
  MAX_STORAGE_GB: "100"

```

**High-Volume (Minimal retention, auto-cleanup):**

```yaml
environment:
  SAVE_ANNOTATED_IMAGES: "true"
  IMAGE_RETENTION_HOURS: "6"
  MAX_STORAGE_GB: "50"

```

## Deployment

### Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models      # ML model
      - ./logs:/app/logs          # Application logs
      - ./outputs:/app/outputs    # Annotated images

```

## Performance Characteristics

- **Detection Time**: 200-500ms per image
- **Image Storage**: +10-20ms overhead
- **Memory Usage**: ~2GB (model + cache)
- **Disk Usage**: ~2-5MB per inspection
- **Concurrent Requests**: Thread-safe
- **Cache Expiration**: 24 hours
- **Image Cleanup**: Automatic (24 hours)

## Security Considerations

### Current Implementation (Testing/Development)

⚠️ **Known Limitations:**

- No authentication/authorization (open API)
- CORS allows all origins (`allow_origins=["*"]`)
- No rate limiting or throttling
- SSRF vulnerability in URL downloads (no URL validation)
- No input sanitization for vehicle_id/inspection_type
- No request signing or verification
- Logs may contain sensitive information

### Production Recommendations

🔒 **Required for Production:**

**Authentication & Authorization:**

- Implement API key authentication (header-based)
- Add JWT tokens for user sessions
- Role-based access control (RBAC)
- OAuth2 integration for enterprise SSO

**Network Security:**

- Restrict CORS to specific domains
- Enable HTTPS/TLS (terminate at load balancer)
- Implement rate limiting (per IP/API key)
- Add request size limits at nginx/load balancer
- Use private networks for internal services

**Input Validation:**

- Whitelist allowed image URLs (domain validation)
- Sanitize all user inputs (vehicle_id, inspection_type)
- Validate file types and magic numbers
- Implement content security policies

**Monitoring & Logging:**

- Structured logging with correlation IDs
- Audit trail for all API calls
- Alert on suspicious patterns
- PII redaction in logs
- SIEM integration

**Data Protection:**

- Encrypt images at rest
- Secure deletion of expired data
- Backup and disaster recovery
- GDPR/compliance considerations

## Scalability & Performance

### Current Capacity

- **Single Instance**: ~10-20 requests/second (CPU)
- **Memory**: ~2GB per instance (model + cache)
- **Storage**: 10GB default (configurable)
- **Bottleneck**: ML inference (200-500ms per image)

### Horizontal Scaling Strategy

```ini
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
   │Instance1│        │Instance2│        │Instance3│
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼───────┐
                    │Shared Storage│
                    │   (NFS/S3)   │
                    └──────────────┘

```

**Scaling Considerations:**

- Use shared storage (NFS/S3) for images across instances
- Implement distributed cache (Redis) for inspection results
- Add message queue (RabbitMQ/SQS) for async processing
- GPU instances for faster inference
- CDN for serving annotated images

### Performance Optimization

- **Model Optimization**: ONNX export, TensorRT, quantization
- **Batch Processing**: Group multiple images per inference
- **Caching**: CDN for frequently accessed images
- **Async Processing**: Background workers for non-urgent requests
- **Image Preprocessing**: Resize before upload (client-side)

## Monitoring & Observability

### Health Checks

- **Endpoint**: `GET /health`
- **Frequency**: Every 30 seconds (Docker healthcheck)
- **Metrics**: Model loaded, cache stats, storage stats

### Key Metrics to Monitor

- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Model inference time
- Cache hit rate
- Storage usage (GB, % of limit)
- Memory usage per instance
- CPU utilization

### Logging Strategy

```python
# Structured logging format
{
  "timestamp": "2025-11-16T10:30:00Z",
  "level": "INFO",
  "service": "inspectify",
  "endpoint": "/detect/upload",
  "inspection_id": "uuid",
  "vehicle_id": "ABC123",
  "processing_time_ms": 245.3,
  "detections": 2,
  "image_enhanced": false
}

```

### Alerting Rules

- Response time > 2 seconds (p95)
- Error rate > 5%
- Storage usage > 80%
- Memory usage > 90%
- Model inference failures
- Health check failures

## Disaster Recovery

### Backup Strategy

- **Images**: Daily backup to S3/cloud storage
- **Configuration**: Version controlled (Git)
- **Model**: Versioned in artifact repository

### Recovery Procedures

1. **Service Failure**: Auto-restart via Docker/Kubernetes
2. **Data Loss**: Restore from latest backup
3. **Model Corruption**: Rollback to previous version
4. **Complete Outage**: Deploy to backup region

### High Availability

- Multi-AZ deployment
- Health check-based routing
- Automatic failover
- Zero-downtime deployments (blue-green)

## Future Architecture Considerations

### Microservices Decomposition

```ini
┌─────────────┐        ┌─────────────┐         ┌─────────────┐
│   API       │────▶  │  Detection  │────▶  │   Storage   │
│  Gateway    │        │   Service   │         │   Service   │
└─────────────┘        └─────────────┘         └─────────────┘
                             │
                      ┌──────▼──────┐
                      │  Enhancement│
                      │   Service   │
                      └─────────────┘

```

### Event-Driven Architecture

- Async processing via message queues
- Event sourcing for audit trail
- CQRS for read/write separation
- Webhook notifications for completion

### Database Integration

- PostgreSQL for inspection metadata
- TimescaleDB for time-series metrics
- Elasticsearch for full-text search
- Redis for distributed caching

### ML Pipeline

- Model versioning (MLflow)
- A/B testing framework
- Continuous training pipeline
- Model performance monitoring
- Automated retraining triggers
