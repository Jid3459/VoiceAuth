"""
Custom Logging System for Voice Auth Application
Only logs from app modules, filters out third-party and Python stdlib logs
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import inspect

class AppLogFilter(logging.Filter):
    """Filter to only show logs from our app modules"""
    
    def __init__(self, app_module: str = "app"):
        super().__init__()
        self.app_module = app_module
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Only allow logs from app modules"""
        # Get the module name
        module_name = record.name
        
        # Only allow logs from our app
        if module_name.startswith(self.app_module):
            return True
        
        # Block all third-party and stdlib logs
        return False


class ColoredFormatter(logging.Formatter):
    """Colored console output for better readability"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


class AppLogger:
    """Custom Application Logger"""
    
    _instance: Optional['AppLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger("app")
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False  # Don't propagate to root logger
            
            # Remove any existing handlers
            self.logger.handlers.clear()
            
            # Add custom filter
            self.logger.addFilter(AppLogFilter("app"))
            
            # Default settings
            self.log_to_console = True
            self.log_to_file = True
            self.log_level = "INFO"
            self.log_file_path = Path("logs/app.log")
            
            # Setup handlers
            self._setup_handlers()
            
            AppLogger._initialized = True
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        # Console Handler
        if self.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level))
            
            console_formatter = ColoredFormatter(
                fmt='%(levelname)s | %(asctime)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.addFilter(AppLogFilter("app"))
            self.logger.addHandler(console_handler)
        
        # File Handler
        if self.log_to_file:
            # Create logs directory if it doesn't exist
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(self.log_file_path, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            
            file_formatter = logging.Formatter(
                fmt='%(levelname)-8s | %(asctime)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(AppLogFilter("app"))
            self.logger.addHandler(file_handler)
    
    def update_settings(
        self,
        log_level: Optional[str] = None,
        log_to_console: Optional[bool] = None,
        log_to_file: Optional[bool] = None,
        enable_debug: Optional[bool] = None
    ):
        """Update logger settings dynamically"""
        if log_level is not None:
            self.log_level = log_level
        
        if log_to_console is not None:
            self.log_to_console = log_to_console
        
        if log_to_file is not None:
            self.log_to_file = log_to_file
        
        if enable_debug is not None:
            self.log_level = "DEBUG" if enable_debug else "INFO"
        
        # Reconfigure handlers
        self.logger.handlers.clear()
        self._setup_handlers()
    
    def get_logger(self, name: str = "app") -> logging.Logger:
        """Get a logger instance for a specific module"""
        return logging.getLogger(name)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)
    
    def get_recent_logs(self, lines: int = 100) -> list:
        """Get recent log entries from file"""
        try:
            if self.log_file_path.exists():
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:]
            return []
        except Exception as e:
            self.error(f"Error reading log file: {e}")
            return []
    
    def clear_logs(self):
        """Clear log file"""
        try:
            if self.log_file_path.exists():
                with open(self.log_file_path, 'w') as f:
                    f.write(f"=== Logs cleared at {datetime.now()} ===\n")
                self.info("Log file cleared")
        except Exception as e:
            self.error(f"Error clearing log file: {e}")


# Singleton instance
app_logger = AppLogger()

# Convenience function
def get_logger(name: str = "app") -> logging.Logger:
    """Get logger instance for a module"""
    return app_logger.get_logger(name)