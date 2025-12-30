# logger.py - SmartFormsGPT Logging Configuration

import os
import sys
from loguru import logger
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Remove default logger
logger.remove()

# Get log level from environment
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/smartforms.log")

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True
)

# Add file handler with rotation
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=log_level,
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)

def get_logger(name: str):
    """Get a logger instance with the specified name."""
    return logger.bind(name=name)

# Export logger
__all__ = ["logger", "get_logger"]
