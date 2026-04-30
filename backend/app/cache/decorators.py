"""
Cache decorators for easy caching
"""

import functools
import hashlib
import json
from typing import Callable, Any
from .cache_manager import cache_manager
from ..logger import get_logger

logger = get_logger(__name__)

def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            cache_key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                cache_key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}={v}")
            
            # Create hash of key parts
            cache_key_str = ":".join(cache_key_parts)
            cache_key = hashlib.md5(cache_key_str.encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator