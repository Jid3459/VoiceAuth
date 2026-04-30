"""
Advanced Rate Limiting Middleware
Prevents abuse and ensures fair usage
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from ..logger import get_logger

logger = get_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiting algorithm
    More sophisticated than simple counter
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.bucket_size = requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        
        # Store: {client_id: (tokens, last_update_time)}
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (self.bucket_size, time.time())
        )
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from request state (if authenticated)
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user_{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip_{client_ip}"
    
    def _refill_bucket(self, client_id: str) -> float:
        """Refill tokens based on time elapsed"""
        tokens, last_update = self.buckets[client_id]
        now = time.time()
        elapsed = now - last_update
        
        # Add tokens based on elapsed time
        tokens = min(self.bucket_size, tokens + elapsed * self.refill_rate)
        
        self.buckets[client_id] = (tokens, now)
        return tokens
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        
        # Refill bucket
        tokens = self._refill_bucket(client_id)
        
        if tokens < 1.0:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": int((1.0 - tokens) / self.refill_rate)
                }
            )
        
        # Consume one token
        tokens, last_update = self.buckets[client_id]
        self.buckets[client_id] = (tokens - 1.0, last_update)
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens - 1))
        
        return response