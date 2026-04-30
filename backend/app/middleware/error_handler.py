"""
Global Error Handler Middleware
Ensures consistent error responses and logging
"""

import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from ..logger import get_logger

logger = get_logger(__name__)

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Catches all exceptions and returns standardized error responses
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            logger.error(traceback.format_exc())
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Database Error",
                    "message": "A database error occurred. Please try again later.",
                    "type": "database_error"
                }
            )
        
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Validation Error",
                    "message": str(e),
                    "type": "validation_error"
                }
            )
        
        except PermissionError as e:
            logger.warning(f"Permission denied: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Permission Denied",
                    "message": str(e),
                    "type": "permission_error"
                }
            )
        
        except FileNotFoundError as e:
            logger.warning(f"Resource not found: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "error": "Not Found",
                    "message": str(e),
                    "type": "not_found_error"
                }
            )
        
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}")
            logger.critical(traceback.format_exc())
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Our team has been notified.",
                    "type": "internal_error"
                }
            )