from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class BoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    width: float
    height: float


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: BoundingBox
    pixel_area: int


class DamageMetrics(BaseModel):
    total_detections: int
    dents: int
    scratches: int
    cracks: int
    broken_lamps: int
    shattered_glass: int
    flat_tires: int
    severity: str
    total_damage_pixels: int


class DetectionRequest(BaseModel):
    image_url: Optional[HttpUrl] = Field(
        None, description="Image URL (optional if uploading file)"
    )
    vehicle_id: str = Field(..., description="Vehicle ID")
    inspection_type: str = Field("departure", description="departure|return")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)
    enable_enhancement: bool = Field(True, description="Apply low-light enhancement")


class DetectionResponse(BaseModel):
    status: str  # success, processing, error
    inspection_id: str
    vehicle_id: str
    timestamp: str
    image_url: Optional[str]
    damage_metrics: Optional[DamageMetrics]
    detections: Optional[List[Detection]]
    processing_time_ms: Optional[float]
    image_enhanced: Optional[bool]
    message: str
