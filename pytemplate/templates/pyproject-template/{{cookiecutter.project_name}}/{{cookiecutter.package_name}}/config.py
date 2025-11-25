import sys
from pathlib import Path

from dynaconf import Dynaconf
from loguru import logger

# Create base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Configure settings with defaults for missing files
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{BASE_DIR}/settings.yaml", f"{BASE_DIR}/.secrets.yaml"],
    environments=True,
    load_dotenv=True,
    dotenv_path=f"{BASE_DIR}/{{cookiecutter.envfile}}",
)

# Default configuration values (used when settings files don't exist)
_DEFAULT_LOG_LEVEL = "INFO"
_DEFAULT_LOG_FILE = f"{BASE_DIR}/logs/app.log"


def setup_logger():
    """Configure loguru logger."""
    # Remove any default handlers
    logger.remove()

    # Get log level with fallback to default
    log_level = settings.get("LOG_LEVEL", _DEFAULT_LOG_LEVEL)
    log_file = settings.get("LOG_FILE", _DEFAULT_LOG_FILE)

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
        level=log_level,
    )

    # Create logs directory if it doesn't exist
    log_path = Path(log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    # Add a file sink with rotation
    logger.add(
        log_file,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="1 week",  # Keep logs for 1 week
        compression="zip",  # Compress rotated logs
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
    )


# Setup logger on module import
setup_logger()
