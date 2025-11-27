"""Logging configuration for the project."""

import os
import sys
import threading
from pathlib import Path

from loguru import logger

# Remove any existing handlers
logger.remove()

# Configure logger format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Add stdout handler with colored output (always enabled)
logger.add(
    sys.stdout,
    colorize=True,
    format=LOG_FORMAT,
    level="INFO",
)

# File logging is optional - only enabled via PYTEMPLATE_DEBUG or --debug flag
_file_handler_id: int | None = None
_file_handler_lock = threading.Lock()


def enable_file_logging() -> None:
    """Enable file logging to user cache directory.

    This creates a log file in the user's cache directory to avoid
    issues with read-only directories or polluting the current directory.
    Thread-safe: uses a lock to prevent race conditions.
    """
    global _file_handler_id

    with _file_handler_lock:
        if _file_handler_id is not None:
            return  # Already enabled

        # Use platform-appropriate cache directory
        if sys.platform == "darwin":
            cache_dir = Path.home() / "Library" / "Logs" / "pytemplate"
        elif sys.platform == "win32":
            # Handle None or empty LOCALAPPDATA gracefully
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                cache_dir = Path(local_app_data) / "pytemplate" / "logs"
            else:
                cache_dir = Path.home() / "AppData" / "Local" / "pytemplate" / "logs"
        else:
            xdg_cache = os.environ.get("XDG_CACHE_HOME")
            if xdg_cache:
                cache_dir = Path(xdg_cache) / "pytemplate"
            else:
                cache_dir = Path.home() / ".cache" / "pytemplate"

        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Log to stderr since file logging failed, but don't crash
            print(f"Warning: Could not create log directory {cache_dir}: {e}", file=sys.stderr)
            return

        log_file = cache_dir / "project_creation.log"

        _file_handler_id = logger.add(
            log_file,
            format=LOG_FORMAT,
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
        )


def disable_file_logging() -> None:
    """Disable file logging. Thread-safe."""
    global _file_handler_id

    with _file_handler_lock:
        if _file_handler_id is not None:
            logger.remove(_file_handler_id)
            _file_handler_id = None


# Auto-enable file logging if PYTEMPLATE_DEBUG is set
if os.environ.get("PYTEMPLATE_DEBUG", "").lower() in ("1", "true", "yes"):
    enable_file_logging()

# Export logger instance
__all__ = ["logger", "enable_file_logging", "disable_file_logging"]
