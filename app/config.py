import os
from pathlib import Path

# Image storage configuration
SAVE_ANNOTATED_IMAGES = os.getenv("SAVE_ANNOTATED_IMAGES", "true").lower() == "true"
IMAGE_RETENTION_HOURS = int(os.getenv("IMAGE_RETENTION_HOURS", "24"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs/inspections"))
MAX_STORAGE_GB = float(os.getenv("MAX_STORAGE_GB", "10"))

# Ensure output directory exists
if SAVE_ANNOTATED_IMAGES:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
