"""Configuration management using Dynaconf.

Usage:
    from {{cookiecutter.package_name}}.config import settings

    # Access configuration values
    log_level = settings.get("LOG_LEVEL", "INFO")
    debug_mode = settings.get("DEBUG", False)
"""

from pathlib import Path

from dynaconf import Dynaconf


# Base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Configure settings with defaults for missing files
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{BASE_DIR}/settings.yaml", f"{BASE_DIR}/.secrets.yaml"],
    environments=True,
    load_dotenv=True,
    dotenv_path=f"{BASE_DIR}/{{cookiecutter.envfile}}",
)

def setup_logger(*args, **kwargs):
    """Deprecated: Import from logger module instead.

    This function has been moved to logger.py for better separation of concerns.
    Please update your imports to: from {{cookiecutter.package_name}}.logger import setup_logger

    Args:
        *args: Positional arguments passed to the new setup_logger.
        **kwargs: Keyword arguments passed to the new setup_logger.

    Returns:
        Result from the new setup_logger function.
    """
    import warnings

    warnings.warn(
        "setup_logger in config.py is deprecated. "
        "Import from {{cookiecutter.package_name}}.logger instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    from .logger import setup_logger as new_setup_logger

    return new_setup_logger(*args, **kwargs)


__all__ = ["settings", "BASE_DIR", "setup_logger"]
