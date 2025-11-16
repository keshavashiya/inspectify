import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from app.config import IMAGE_RETENTION_HOURS, MAX_STORAGE_GB, OUTPUT_DIR

logger = logging.getLogger(__name__)


class ImageStorage:
    """Handles storage and retrieval of annotated images"""

    def __init__(self, base_dir: Path = OUTPUT_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_inspection_images(
        self,
        inspection_id: str,
        original_image: np.ndarray,
        annotated_image: np.ndarray,
        metadata: dict,
    ) -> bool:
        """Save original, annotated images and metadata"""
        try:
            inspection_dir = self.base_dir / inspection_id
            inspection_dir.mkdir(parents=True, exist_ok=True)

            # Save original image
            original_path = inspection_dir / "original.jpg"
            cv2.imwrite(str(original_path), original_image)

            # Save annotated image
            annotated_path = inspection_dir / "annotated.jpg"
            cv2.imwrite(str(annotated_path), annotated_image)

            # Save metadata
            metadata_path = inspection_dir / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved images for inspection: {inspection_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save images for {inspection_id}: {e}")
            return False

    def get_annotated_image(self, inspection_id: str) -> Optional[np.ndarray]:
        """Retrieve annotated image"""
        try:
            image_path = self.base_dir / inspection_id / "annotated.jpg"
            if not image_path.exists():
                return None

            image = cv2.imread(str(image_path))
            return image

        except Exception as e:
            logger.error(f"Failed to load image for {inspection_id}: {e}")
            return None

    def get_original_image(self, inspection_id: str) -> Optional[np.ndarray]:
        """Retrieve original image"""
        try:
            image_path = self.base_dir / inspection_id / "original.jpg"
            if not image_path.exists():
                return None

            image = cv2.imread(str(image_path))
            return image

        except Exception as e:
            logger.error(f"Failed to load original image for {inspection_id}: {e}")
            return None

    def get_metadata(self, inspection_id: str) -> Optional[dict]:
        """Retrieve metadata"""
        try:
            metadata_path = self.base_dir / inspection_id / "metadata.json"
            if not metadata_path.exists():
                return None

            with open(metadata_path, "r") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load metadata for {inspection_id}: {e}")
            return None

    def delete_inspection(self, inspection_id: str) -> bool:
        """Delete all files for an inspection"""
        try:
            inspection_dir = self.base_dir / inspection_id
            if inspection_dir.exists():
                shutil.rmtree(inspection_dir)
                logger.info(f"Deleted inspection directory: {inspection_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete inspection {inspection_id}: {e}")
            return False

    def cleanup_old_inspections(self, max_age_hours: int = IMAGE_RETENTION_HOURS) -> int:
        """Remove inspections older than max_age_hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            deleted_count = 0

            for inspection_dir in self.base_dir.iterdir():
                if not inspection_dir.is_dir():
                    continue

                # Check directory creation time
                dir_mtime = datetime.fromtimestamp(inspection_dir.stat().st_mtime)
                if dir_mtime < cutoff_time:
                    shutil.rmtree(inspection_dir)
                    deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old inspection directories")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old inspections: {e}")
            return 0

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            total_size = 0
            inspection_count = 0

            for inspection_dir in self.base_dir.iterdir():
                if inspection_dir.is_dir():
                    inspection_count += 1
                    for file in inspection_dir.rglob("*"):
                        if file.is_file():
                            total_size += file.stat().st_size

            size_gb = total_size / (1024**3)
            size_mb = total_size / (1024**2)

            return {
                "total_inspections": inspection_count,
                "total_size_mb": round(size_mb, 2),
                "total_size_gb": round(size_gb, 4),
                "max_storage_gb": MAX_STORAGE_GB,
                "usage_percent": round((size_gb / MAX_STORAGE_GB) * 100, 2),
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "total_inspections": 0,
                "total_size_mb": 0,
                "total_size_gb": 0,
                "max_storage_gb": MAX_STORAGE_GB,
                "usage_percent": 0,
            }


# Global storage instance
image_storage = ImageStorage()
