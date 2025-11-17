import logging
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class YOLO11mDetector:
    def __init__(
        self, model_path: str = "models/yolo11m_trained.pt", device: str = None
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO(model_path)
        self.model.to(self.device)

        self.class_names = {
            0: "dent",
            1: "scratch",
            2: "crack",
            3: "broken_lamp",
            4: "shattered_glass",
            5: "flat_tire",
        }

        logger.info(f"YOLO11m loaded on {self.device}")

    def predict(
        self,
        image_array: np.ndarray,
        conf: float = 0.5,
        iou: float = 0.5,
        imgsz: int = 1280,
        augment: bool = False,
        agnostic_nms: bool = False,
        class_thresholds: Optional[Dict[str, float]] = None,
    ) -> Tuple[List[Dict], np.ndarray]:
        results = self.model(
            image_array,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            augment=augment,
            agnostic_nms=agnostic_nms,
            verbose=False,
        )

        if not results:
            return [], image_array

        result = results[0]
        detections = []

        for box in result.boxes:
            detection = {
                "class_id": int(box.cls[0]),
                "class_name": self.class_names.get(int(box.cls[0]), "unknown"),
                "confidence": float(box.conf[0]),
                "bbox": {
                    "x_min": float(box.xyxy[0][0]),
                    "y_min": float(box.xyxy[0][1]),
                    "x_max": float(box.xyxy[0][2]),
                    "y_max": float(box.xyxy[0][3]),
                    "width": float(box.xyxy[0][2] - box.xyxy[0][0]),
                    "height": float(box.xyxy[0][3] - box.xyxy[0][1]),
                },
                "pixel_area": int(
                    (box.xyxy[0][2] - box.xyxy[0][0])
                    * (box.xyxy[0][3] - box.xyxy[0][1])
                ),
            }
            th = None
            if class_thresholds is not None:
                th = class_thresholds.get(detection["class_name"])  
            if th is not None and detection["confidence"] < th:
                pass
            else:
                detections.append(detection)

        annotated_image = result.plot()
        return detections, annotated_image

    def calculate_metrics(self, detections: List[Dict]) -> Dict[str, int]:
        class_counts = {name: 0 for name in self.class_names.values()}
        total_pixels = 0

        for detection in detections:
            class_name = detection["class_name"]
            class_counts[class_name] += 1
            total_pixels += detection["pixel_area"]

        if total_pixels == 0:
            severity = "none"
        elif total_pixels < 5000:
            severity = "minor"
        elif total_pixels < 20000:
            severity = "moderate"
        else:
            severity = "severe"

        return {
            "total_detections": len(detections),
            "dents": class_counts["dent"],
            "scratches": class_counts["scratch"],
            "cracks": class_counts["crack"],
            "broken_lamps": class_counts["broken_lamp"],
            "shattered_glass": class_counts["shattered_glass"],
            "flat_tires": class_counts["flat_tire"],
            "severity": severity,
            "total_damage_pixels": total_pixels,
        }
