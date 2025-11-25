"""Constants module for pytemplate."""

from pathlib import Path


class SecurityError(Exception):
    """Raised when a security violation is detected."""

    pass


# Base paths
PACKAGE_ROOT = Path(__file__).parent


# Template paths
def _find_template_paths_file() -> Path:
    """Find the template_paths.yaml file in either the package directory or installed location."""
    # First try the package directory (for development)
    package_path = PACKAGE_ROOT.parent / "template_paths.yaml"
    if package_path.exists():
        return package_path

    # Then try the installed location
    installed_path = PACKAGE_ROOT / "template_paths.yaml"
    if installed_path.exists():
        return installed_path

    # If neither exists, return the package directory path as default
    return package_path


TEMPLATE_PATHS_FILE = _find_template_paths_file()


def _get_base_dir() -> Path:
    """Get the base directory for templates."""
    # First try the package directory (for development)
    package_dir = PACKAGE_ROOT.parent
    if (package_dir / "templates").exists():
        return package_dir

    # Then try the installed location
    installed_dir = PACKAGE_ROOT
    if (installed_dir / "templates").exists():
        return installed_dir

    # If neither exists, return the package directory as default
    return package_dir


BASE_DIR = _get_base_dir()
