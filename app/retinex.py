import logging
from typing import Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class RetinexEnhancer:
    def __init__(self):
        pass

    def enhance_if_needed(
        self, image: np.ndarray, brightness_threshold: int = 110
    ) -> Tuple[np.ndarray, bool]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)

        if brightness >= brightness_threshold:
            return image, False

        logger.info(
            f"Low-light detected (brightness={brightness:.1f}), applying enhancement"
        )
        return self._enhance_with_clahe(image), True

    def _enhance_with_clahe(self, image: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        lab_enhanced = cv2.merge([l_enhanced, a, b])
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        return enhanced
