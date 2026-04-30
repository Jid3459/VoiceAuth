"""
Request Logging Middleware
Logs all incoming requests and responses for monitoring
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ..logger import get_logger

logger = get_logger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs request details and performance metrics
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Log incoming request
        logger.info(f"→ {method} {path} from {client_ip}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        status_code = response.status_code
        log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
        
        log_message = f"← {method} {path} - {status_code} - {duration:.3f}s"
        
        if log_level == "info":
            logger.info(log_message)
        elif log_level == "warning":
            logger.warning(log_message)
        else:
            logger.error(log_message)
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response