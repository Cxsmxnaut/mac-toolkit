"""Logging system for Mac Toolkit."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class ToolkitLogger:
    """Centralized logging system with timestamps and debug mode support."""
    
    def __init__(self, log_dir: str = "logs", debug: bool = False):
        """Initialize the logger.
        
        Args:
            log_dir: Directory to store log files
            debug: Enable debug mode for verbose logging
        """
        self.log_dir = Path(log_dir)
        self._debug_mode = debug
        self.logger = logging.getLogger("mactoolkit")
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler
        log_file = self.log_dir / f"mactoolkit_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, *args) -> None:
        """Log info message."""
        self.logger.info(message, *args)
    
    def debug(self, message: str, *args) -> None:
        """Log debug message."""
        self.logger.debug(message, *args)
    
    def warning(self, message: str, *args) -> None:
        """Log warning message."""
        self.logger.warning(message, *args)
    
    def error(self, message: str, *args) -> None:
        """Log error message."""
        self.logger.error(message, *args)
    
    def critical(self, message: str, *args) -> None:
        """Log critical message."""
        self.logger.critical(message, *args)
    
    def set_debug(self, debug: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = debug
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.DEBUG if debug else logging.INFO)


# Global logger instance
_logger_instance: Optional[ToolkitLogger] = None


def get_logger(debug: bool = False) -> ToolkitLogger:
    """Get or create the global logger instance.
    
    Args:
        debug: Enable debug mode
        
    Returns:
        ToolkitLogger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ToolkitLogger(debug=debug)
    return _logger_instance
