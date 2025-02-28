"""Constants module for pytemplate."""

from pathlib import Path

class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass

# Base paths
PACKAGE_ROOT = Path(__file__).parent
CONFIG_DIR = PACKAGE_ROOT.parent / "config_templates"

# Template paths
TEMPLATE_PATHS_FILE = PACKAGE_ROOT.parent / "template_paths.yaml"
DEFAULT_USER_CONFIG_DIR = Path.home() / ".pytemplate"
DEFAULT_USER_CONFIG_FILE = DEFAULT_USER_CONFIG_DIR / "config.yaml"

# Environment variables
ENV_BASE_DIR = "PYTEMPLATE_BASE_DIR"
ENV_CUSTOM_TEMPLATES_DIR = "PYTEMPLATE_CUSTOM_TEMPLATES_DIR"
