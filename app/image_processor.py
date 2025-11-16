import logging
from typing import Tuple

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self, max_size_mb: int = 50):
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def download_from_url(self, image_url: str) -> np.ndarray:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            if len(response.content) > self.max_size_bytes:
                raise ValueError(f"Image too large")

            image_array = np.frombuffer(response.content, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Failed to decode image")

            return image
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            raise

    def process_uploaded_file(self, file_bytes: bytes) -> np.ndarray:
        if len(file_bytes) > self.max_size_bytes:
            raise ValueError(f"Image too large")

        image_array = np.frombuffer(file_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        return image

    def get_image_metadata(self, image: np.ndarray) -> dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return {
            "width": image.shape[1],
            "height": image.shape[0],
            "brightness": float(np.mean(gray)),
            "is_low_light": np.mean(gray) < 90,
        }

    def resize_if_needed(self, image: np.ndarray, max_width: int = 1280) -> np.ndarray:
        if image.shape[1] <= max_width:
            return image

        scale = max_width / image.shape[1]
        new_size = (max_width, int(image.shape[0] * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_LINEAR)
