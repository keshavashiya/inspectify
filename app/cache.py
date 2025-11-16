import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache for inspection results"""

    def __init__(self, max_age_minutes: int = 24 * 60):
        self.storage: Dict[str, Dict[str, Any]] = {}
        self.max_age = timedelta(minutes=max_age_minutes)
        self.lock = threading.Lock()

    def save(self, inspection_id: str, data: Dict[str, Any]) -> None:
        """Save inspection result"""
        with self.lock:
            self.storage[inspection_id] = {
                "data": data,
                "created_at": datetime.utcnow(),
            }
            logger.info(f"Cached inspection: {inspection_id}")

    def get(self, inspection_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve inspection result"""
        with self.lock:
            if inspection_id not in self.storage:
                return None

            entry = self.storage[inspection_id]

            # Check if expired
            if datetime.utcnow() - entry["created_at"] > self.max_age:
                del self.storage[inspection_id]
                logger.info(f"Expired inspection: {inspection_id}")
                return None

            return entry["data"]

    def exists(self, inspection_id: str) -> bool:
        """Check if inspection exists"""
        return self.get(inspection_id) is not None

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self.lock:
            now = datetime.utcnow()
            expired_keys = [
                key
                for key, entry in self.storage.items()
                if now - entry["created_at"] > self.max_age
            ]

            for key in expired_keys:
                del self.storage[key]

            logger.info(f"Cleaned up {len(expired_keys)} expired inspections")
            return len(expired_keys)

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        with self.lock:
            return {
                "total_inspections": len(self.storage),
                "storage_size_approx_mb": len(json.dumps(self.storage)) / 1024 / 1024,
            }


# Global cache instance
inspection_cache = InMemoryCache(max_age_minutes=1440)  # 24 hours
