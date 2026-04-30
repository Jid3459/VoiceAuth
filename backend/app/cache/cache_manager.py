"""
In-Memory Cache Manager
Thread-safe caching with TTL support
"""

import time
import threading
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from ..logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """
    Thread-safe in-memory cache with TTL
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                logger.debug(f"Cache MISS: {key}")
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry['expires_at'] and datetime.now() > entry['expires_at']:
                del self._cache[key]
                self._stats['misses'] += 1
                logger.debug(f"Cache EXPIRED: {key}")
                return None
            
            self._stats['hits'] += 1
            logger.debug(f"Cache HIT: {key}")
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
            
            self._cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }
            
            self._stats['sets'] += 1
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                logger.debug(f"Cache DELETE: {key}")
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache CLEARED: {count} entries removed")
    
    def cleanup_expired(self):
        """Remove expired entries"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry['expires_at'] and now > entry['expires_at']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cache CLEANUP: {len(expired_keys)} expired entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self._stats,
                'total_requests': total_requests,
                'hit_rate': round(hit_rate, 2),
                'cache_size': len(self._cache)
            }

# Singleton instance
cache_manager = CacheManager()

# Background cleanup task
def _cleanup_task():
    """Periodic cleanup of expired cache entries"""
    import time
    while True:
        time.sleep(300)  # Every 5 minutes
        cache_manager.cleanup_expired()

# Start cleanup thread
cleanup_thread = threading.Thread(target=_cleanup_task, daemon=True)
cleanup_thread.start()