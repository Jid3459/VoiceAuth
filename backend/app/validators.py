"""
Input validation utilities
"""

import re
from typing import Optional
from fastapi import HTTPException
from .logger import get_logger

logger = get_logger(__name__)

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username (3-30 alphanumeric characters)"""
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(password) > 100:
            return False, "Password must be less than 100 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def validate_audio_file(file_size: int, max_size_mb: int = 10) -> bool:
        """Validate audio file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def sanitize_query(query: str) -> str:
        """Sanitize user query to prevent injection attacks"""
        # Remove potentially dangerous characters
        dangerous_chars = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        
        sanitized = query
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate transaction amount"""
        return 0 < amount <= 1000000  # Max 10 lakh

validator = Validator()