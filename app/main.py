import logging
import os
import threading
import time
import uuid
from datetime import datetime
from typing import Optional

import cv2
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.cache import inspection_cache
from app.config import SAVE_ANNOTATED_IMAGES, CLASS_CONF_THRESHOLDS, MODEL_PATH, MODEL_URL
import requests
from app.detection import YOLO11mDetector
from app.image_processor import ImageProcessor
from app.image_storage import image_storage
from app.models import (
    BoundingBox,
    DamageMetrics,
    Detection,
    DetectionRequest,
    DetectionResponse,
)
from app.retinex import RetinexEnhancer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Inspectify",
    description="AI-powered vehicle damage detection and inspection system using YOLO11m",
    version="1.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
detector = None
image_processor = None
retinex_enhancer = None


@app.on_event("startup")
async def startup_event():
    global detector, image_processor, retinex_enhancer

    logger.info("Initializing services...")

    try:
        model_path = str(MODEL_PATH)
        if MODEL_URL and not os.path.exists(model_path):
            r = requests.get(MODEL_URL, stream=True, timeout=60)
            r.raise_for_status()
            with open(model_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        detector = YOLO11mDetector(model_path=model_path)
        image_processor = ImageProcessor(max_size_mb=50)
        retinex_enhancer = RetinexEnhancer()

        logger.info("✅ All services initialized")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cache_stats = inspection_cache.get_stats()
    storage_stats = image_storage.get_storage_stats() if SAVE_ANNOTATED_IMAGES else {}
    
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "cache_stats": cache_stats,
        "storage_stats": storage_stats,
        "image_storage_enabled": SAVE_ANNOTATED_IMAGES,
    }


@app.post("/detect", response_model=DetectionResponse)
async def detect_damage_from_url(request: DetectionRequest):
    """
    Detect vehicle damage from URL - SYNCHRONOUS (returns results immediately)

    Request:
    {
        "image_url": "https://example.com/car.jpg",
        "vehicle_id": "XYZ123",
        "inspection_type": "departure",
        "confidence_threshold": 0.5,
        "enable_enhancement": true
    }
    """
    start_time = time.time()
    inspection_id = str(uuid.uuid4())

    try:
        # Download image
        logger.info(f"Downloading image from URL: {request.image_url}")
        image = image_processor.download_from_url(str(request.image_url))

        # Get metadata
        metadata = image_processor.get_image_metadata(image)
        logger.info(f"Image metadata: {metadata}")

        # Resize if needed
        image = image_processor.resize_if_needed(image)

        # Apply enhancement if needed
        image_enhanced = False
        if request.enable_enhancement:
            image, image_enhanced = retinex_enhancer.enhance_if_needed(image)

        # Run inference
        detections, annotated_image = detector.predict(
            image,
            conf=request.confidence_threshold,
            iou=request.iou_threshold,
            imgsz=request.img_size,
            augment=request.enable_tta,
            agnostic_nms=request.agnostic_nms,
            class_thresholds=CLASS_CONF_THRESHOLDS,
        )
        metrics = detector.calculate_metrics(detections)

        # Format response
        detection_objects = [
            Detection(
                class_name=d["class_name"],
                confidence=d["confidence"],
                bbox=BoundingBox(
                    x_min=d["bbox"]["x_min"],
                    y_min=d["bbox"]["y_min"],
                    x_max=d["bbox"]["x_max"],
                    y_max=d["bbox"]["y_max"],
                    width=d["bbox"]["width"],
                    height=d["bbox"]["height"],
                ),
                pixel_area=d["pixel_area"],
            )
            for d in detections
        ]

        damage_metrics = DamageMetrics(**metrics)
        processing_time = (time.time() - start_time) * 1000

        response = DetectionResponse(
            status="success",
            inspection_id=inspection_id,
            vehicle_id=request.vehicle_id,
            timestamp=datetime.utcnow().isoformat(),
            image_url=str(request.image_url),
            damage_metrics=damage_metrics,
            detections=detection_objects,
            processing_time_ms=processing_time,
            image_enhanced=image_enhanced,
            message=f"Detection complete: {len(detections)} damage(s) found",
        )

        # Cache result for later retrieval
        inspection_cache.save(inspection_id, response.dict())

        # Save annotated images if enabled
        if SAVE_ANNOTATED_IMAGES:
            image_storage.save_inspection_images(
                inspection_id=inspection_id,
                original_image=image,
                annotated_image=annotated_image,
                metadata={
                    "vehicle_id": request.vehicle_id,
                    "timestamp": response.timestamp,
                    "image_url": str(request.image_url),
                    "detections_count": len(detections),
                    "image_enhanced": image_enhanced,
                },
            )

        logger.info(
            f"✅ Detection complete in {processing_time:.1f}ms - ID: {inspection_id}"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/upload", response_model=DetectionResponse)
async def detect_damage_from_upload(
    file: UploadFile = File(...),
    vehicle_id: str = "unknown",
    inspection_type: str = "departure",
    confidence_threshold: float = 0.5,
    enable_enhancement: bool = True,
):
    """
    Detect vehicle damage from uploaded file - SYNCHRONOUS

    Form parameters:
    - file: Image file (.jpg, .png)
    - vehicle_id: Vehicle ID
    - inspection_type: departure|return
    - confidence_threshold: 0.0-1.0
    - enable_enhancement: true|false
    """
    start_time = time.time()
    inspection_id = str(uuid.uuid4())

    try:
        # Read file
        content = await file.read()
        logger.info(f"Processing uploaded file: {file.filename} ({len(content)} bytes)")

        image = image_processor.process_uploaded_file(content)

        # Get metadata
        metadata = image_processor.get_image_metadata(image)
        logger.info(f"Image metadata: {metadata}")

        # Resize if needed
        image = image_processor.resize_if_needed(image)

        # Apply enhancement if needed
        image_enhanced = False
        if enable_enhancement:
            image, image_enhanced = retinex_enhancer.enhance_if_needed(image)

        # Run inference
        detections, annotated_image = detector.predict(
            image,
            conf=confidence_threshold,
            iou=0.5,
            imgsz=1280,
            augment=False,
            agnostic_nms=False,
            class_thresholds=CLASS_CONF_THRESHOLDS,
        )
        metrics = detector.calculate_metrics(detections)

        # Format response
        detection_objects = [
            Detection(
                class_name=d["class_name"],
                confidence=d["confidence"],
                bbox=BoundingBox(
                    x_min=d["bbox"]["x_min"],
                    y_min=d["bbox"]["y_min"],
                    x_max=d["bbox"]["x_max"],
                    y_max=d["bbox"]["y_max"],
                    width=d["bbox"]["width"],
                    height=d["bbox"]["height"],
                ),
                pixel_area=d["pixel_area"],
            )
            for d in detections
        ]

        damage_metrics = DamageMetrics(**metrics)
        processing_time = (time.time() - start_time) * 1000

        response = DetectionResponse(
            status="success",
            inspection_id=inspection_id,
            vehicle_id=vehicle_id,
            timestamp=datetime.utcnow().isoformat(),
            image_url=f"local:{file.filename}",
            damage_metrics=damage_metrics,
            detections=detection_objects,
            processing_time_ms=processing_time,
            image_enhanced=image_enhanced,
            message=f"Detection complete: {len(detections)} damage(s) found",
        )

        # Cache result
        inspection_cache.save(inspection_id, response.dict())

        # Save annotated images if enabled
        if SAVE_ANNOTATED_IMAGES:
            image_storage.save_inspection_images(
                inspection_id=inspection_id,
                original_image=image,
                annotated_image=annotated_image,
                metadata={
                    "vehicle_id": vehicle_id,
                    "timestamp": response.timestamp,
                    "filename": file.filename,
                    "detections_count": len(detections),
                    "image_enhanced": image_enhanced,
                },
            )

        logger.info(
            f"✅ Detection complete in {processing_time:.1f}ms - ID: {inspection_id}"
        )
        return response

    except Exception as e:
        logger.error(f"❌ Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{inspection_id}")
async def get_inspection_results(inspection_id: str):
    """
    Retrieve inspection results by ID

    Returns the previously processed inspection result
    """
    try:
        result = inspection_cache.get(inspection_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Inspection {inspection_id} not found or expired",
            )

        logger.info(f"Retrieved cached inspection: {inspection_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving inspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_stats": inspection_cache.get_stats(),
        "note": "Inspections expire after 24 hours",
    }


@app.post("/cache/cleanup")
async def cleanup_cache():
    """Manually cleanup expired entries"""
    cleaned_cache = inspection_cache.cleanup_expired()
    cleaned_images = 0
    
    if SAVE_ANNOTATED_IMAGES:
        cleaned_images = image_storage.cleanup_old_inspections()
    
    return {
        "status": "success",
        "cleaned_cache_entries": cleaned_cache,
        "cleaned_image_directories": cleaned_images,
    }


@app.get("/results/{inspection_id}/image")
async def get_inspection_image(inspection_id: str, image_type: str = "annotated"):
    """
    Retrieve inspection image by ID
    
    Parameters:
    - inspection_id: Inspection UUID
    - image_type: 'annotated' (default) or 'original'
    
    Returns the image as JPEG
    """
    if not SAVE_ANNOTATED_IMAGES:
        raise HTTPException(
            status_code=503,
            detail="Image storage is disabled",
        )
    
    try:
        if image_type == "original":
            image = image_storage.get_original_image(inspection_id)
        else:
            image = image_storage.get_annotated_image(inspection_id)
        
        if image is None:
            raise HTTPException(
                status_code=404,
                detail=f"Image not found for inspection {inspection_id}",
            )
        
        # Encode image as JPEG
        _, buffer = cv2.imencode('.jpg', image)
        
        return Response(
            content=buffer.tobytes(),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": f"inline; filename={inspection_id}_{image_type}.jpg"
            },
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{inspection_id}/metadata")
async def get_inspection_metadata(inspection_id: str):
    """
    Retrieve inspection metadata
    
    Returns stored metadata including vehicle_id, timestamp, etc.
    """
    if not SAVE_ANNOTATED_IMAGES:
        raise HTTPException(
            status_code=503,
            detail="Image storage is disabled",
        )
    
    try:
        metadata = image_storage.get_metadata(inspection_id)
        
        if metadata is None:
            raise HTTPException(
                status_code=404,
                detail=f"Metadata not found for inspection {inspection_id}",
            )
        
        return metadata
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/results/{inspection_id}")
async def delete_inspection(inspection_id: str):
    """
    Delete inspection data (cache + images)
    
    Removes both cached results and stored images
    """
    try:
        # Remove from cache
        cache_result = inspection_cache.get(inspection_id)
        cache_deleted = cache_result is not None
        
        # Remove images if storage is enabled
        images_deleted = False
        if SAVE_ANNOTATED_IMAGES:
            images_deleted = image_storage.delete_inspection(inspection_id)
        
        if not cache_deleted and not images_deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Inspection {inspection_id} not found",
            )
        
        return {
            "status": "success",
            "inspection_id": inspection_id,
            "cache_deleted": cache_deleted,
            "images_deleted": images_deleted,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))
