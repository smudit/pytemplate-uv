"""Logger module providing opt-in loguru configuration.

Usage:
    from {{cookiecutter.package_name}}.logger import logger, setup_logger

    # Optional: call setup_logger() to configure handlers
    setup_logger()

    # Use logger as normal
    logger.info("Application started")
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logger(
    log_level: str | None = None,
    log_file: str | None = None,
    colorize: bool = True,
) -> None:
    """Configure loguru logger with console and optional file output.

    If log_level or log_file are not provided, attempts to read from Dynaconf settings.
    Falls back to sensible defaults if settings are not configured.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            If None, reads from settings.LOG_LEVEL or defaults to "INFO".
        log_file: Optional path to log file. If provided, logs will also be written to file.
            If None, reads from settings.LOG_FILE.
        colorize: Whether to use colored output for console logging.
    """
    # Try to read from settings if not provided
    if log_level is None or log_file is None:
        try:
            from .config import settings

            if log_level is None:
                log_level = settings.get("LOG_LEVEL", "INFO")
            if log_file is None:
                log_file = settings.get("LOG_FILE", None)
        except Exception:
            # If settings not available, use defaults
            if log_level is None:
                log_level = "INFO"
    # Remove any existing handlers
    logger.remove()

    # Console handler
    logger.add(
        sys.stdout,
        colorize=colorize,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=log_level,
    )

    # File handler (optional)
    if log_file:
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=log_level,
        )


# Export logger for direct use
__all__ = ["logger", "setup_logger"]
