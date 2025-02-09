"""Logging configuration for the project."""

import sys

from loguru import logger

# Configure logger with rotation
logger.add(
    "project_creation.log", format="{time} {level} {message}", level="INFO", rotation="10 MB"
)
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

# Export logger instance
__all__ = ["logger"]
