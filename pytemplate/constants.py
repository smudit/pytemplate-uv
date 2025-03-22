"""Constants module for pytemplate."""

from pathlib import Path

class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass

# Base paths
PACKAGE_ROOT = Path(__file__).parent

# Template paths
TEMPLATE_PATHS_FILE = PACKAGE_ROOT.parent / "template_paths.yaml"

