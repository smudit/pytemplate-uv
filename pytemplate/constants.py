"""Constants module for pytemplate."""

from pathlib import Path

# Base paths
PACKAGE_ROOT = Path(__file__).parent
CONFIG_DIR = PACKAGE_ROOT / "config"

# Template paths
TEMPLATE_PATHS_FILE = CONFIG_DIR / "template_paths.yaml"
DEFAULT_USER_CONFIG_DIR = Path.home() / ".pytemplate"
DEFAULT_USER_CONFIG_FILE = DEFAULT_USER_CONFIG_DIR / "config.yaml"

# Environment variables
ENV_BASE_DIR = "PYTEMPLATE_BASE_DIR"
ENV_CUSTOM_TEMPLATES_DIR = "PYTEMPLATE_CUSTOM_TEMPLATES_DIR"