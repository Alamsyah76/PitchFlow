"""
Logger Utility Module
Configures and provides centralized logging for the backend
"""

import logging
import sys
from typing import Optional


class LoggerConfig:
    """Centralized logging configuration."""
    
    _loggers = {}
    
    @staticmethod
    def setup_logger(
        name: str, 
        level: str = "INFO",
        log_file: Optional[str] = None
    ) -> logging.Logger:
        """
        Setup and return a configured logger instance.
        
        Args:
            name: Logger name (typically __name__)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            
        Returns:
            Configured logger instance
        """
        if name in LoggerConfig._loggers:
            return LoggerConfig._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            logger.addHandler(console_handler)
            
            # File handler if specified
            if log_file:
                try:
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
                    file_handler.setFormatter(formatter)
                    logger.addHandler(file_handler)
                except Exception as e:
                    logger.warning(f"Could not create file handler: {e}")
        
        LoggerConfig._loggers[name] = logger
        return logger


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return LoggerConfig.setup_logger(name)
