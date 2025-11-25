import sys
from pathlib import Path

from dynaconf import Dynaconf
from loguru import logger

# Create base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Configure settings
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{BASE_DIR}/settings.yaml", f"{BASE_DIR}/.secrets.yaml"],
    environments=True,
    load_dotenv=True,
)


def setup_logger():
    """Configure loguru logger."""
    # Remove any default handlers
    logger.remove()

    # Set custom log level colors
    logger.level("DEBUG", color="<blue>")
    logger.level("INFO", color="<green>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<red>")
    logger.level("CRITICAL", color="<bold><red>")

    # Add a console sink (stdout) with color
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )

    # Create logs directory if it doesn't exist
    log_path = Path(settings.LOG_FILE).parent
    log_path.mkdir(parents=True, exist_ok=True)

    # Add a file sink with rotation
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="1 week",  # Keep logs for 1 week
        compression="zip",  # Compress rotated logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL,
    )


# Setup logger on module import
setup_logger()
