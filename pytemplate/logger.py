"""Logging configuration for the project."""

import sys

from loguru import logger

# Remove any existing handlers
logger.remove()

# Configure logger with rotation
logger.add(
    "project_creation.log",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    rotation="10 MB",
)

# Add stdout handler with colored output
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

# Export logger instance
__all__ = ["logger"]
