"""Template management module for handling template resolution and customization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .constants import (
    TEMPLATE_PATHS_FILE,
)
from .logger import logger


class TemplateResolver:
    """Handles template resolution and path management."""

    def _resolve_template_path(self, template_path: str) -> Path:
        """Resolve a template path to an absolute path.

        Args:
        ----
            template_path: The template path to resolve.

        Returns:
        -------
            The absolute path to the template.

        """
        # If it's a GitHub repository, return as is
        if template_path.startswith("gh:"):
            logger.debug(f"Using GitHub repository: {template_path}")
            return Path(template_path)

        # For local paths, ensure they're relative to the package directory
        package_dir = Path(__file__).parent
        resolved_path = package_dir / template_path

        logger.debug(f"Resolved '{template_path}' to '{resolved_path}'")
        return resolved_path

    def __init__(self, config_path: str | None = None):
        """Initialize template resolver.

        Args:
        ----
            config_path (Optional[str]): Path to config file. If None, uses default locations.

        """
        logger.debug(f"Initializing TemplateResolver with config_path: {config_path}")
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.base_dir = self._get_base_dir()
        logger.info(f"Using base directory: {self.base_dir}")
        self.template_paths = self._load_template_paths()
        self.config = self._load_config()
        logger.debug("TemplateResolver initialization complete")

    def _get_default_config_path(self) -> Path:
        """Get default configuration path."""
        return TEMPLATE_PATHS_FILE

    def _get_base_dir(self) -> Path:
        """Get base directory - uses package directory."""
        # Get the directory containing the package
        package_dir = Path(__file__).resolve().parent.parent
        logger.debug(f"Package directory resolved to: {package_dir}")
        return package_dir

    def _load_template_paths(self) -> dict[str, Any]:
        """Load template paths from YAML file.

        Returns
        -------
            Dict[str, Any]: Template paths configuration.

        Raises
        ------
            FileNotFoundError: If template paths file doesn't exist.
            yaml.YAMLError: If template paths file is invalid YAML.

        """
        try:
            with TEMPLATE_PATHS_FILE.open() as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Template paths file not found: {TEMPLATE_PATHS_FILE}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing template paths file: {e}")
            raise

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file.

        Returns
        -------
            Dict[str, Any]: Configuration dictionary.

        Raises
        ------
            FileNotFoundError: If config file doesn't exist and can't be created.
            yaml.YAMLError: If config file is invalid YAML.

        """
        logger.debug(f"Loading config from: {self.config_path}")

        # If config_path is the same as TEMPLATE_PATHS_FILE, use template_paths directly
        if self.config_path == TEMPLATE_PATHS_FILE:
            logger.debug(
                "Config path is same as template paths file, using template_paths directly"
            )
            return self.template_paths

        if not self.config_path.exists():
            logger.info(f"Config file not found, creating default at: {self.config_path}")
            # Create default config
            try:
                with self.config_path.open("x") as f:  # Atomic create using 'x' mode
                    default_config = {
                        "base_dir": str(self.base_dir),
                        "template_paths": self.template_paths,
                    }
                    yaml.safe_dump(default_config, f)
            except FileExistsError:
                pass  # File was created by another process
            except OSError as e:
                logger.error(f"Failed to create config: {e}")
                raise

        try:
            with self.config_path.open() as f:
                config = yaml.safe_load(f)
                logger.debug(f"Loaded config with {len(config)} entries")
            return config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise

    def get_template_path(self, template_type: str, template_name: str) -> Path:
        """Get full path for a template.

        Args:
        ----
            template_type (str): Type of template (e.g., 'project_templates', 'config_templates').
            template_name (str): Name of the template.

        Returns:
        -------
            Path: Full path to the template.

        Raises:
        ------
            ValueError: If template type or name is not found in config,
                       or if resolved path is outside base directory.

        """
        logger.debug(f"Resolving path for template: {template_type}/{template_name}")
        relative_path = self._get_relative_path(template_type, template_name)
        resolved_path = self._resolve_template_path(relative_path)
        logger.debug(f"Resolved template path: {resolved_path}")
        return resolved_path

    def _get_relative_path(self, template_type: str, template_name: str) -> str:
        """Get relative path from config.

        Args:
        ----
            template_type (str): Type of template.
            template_name (str): Name of the template.

        Returns:
        -------
            str: Relative path to the template.

        Raises:
        ------
            ValueError: If template type or name is not found.

        """
        try:
            # Access template_type directly from the config structure
            if template_type not in self.config:
                available_types = ", ".join(self.config.keys())
                raise ValueError(
                    f"Template type '{template_type}' not found. Available types: {available_types}"
                )

            template_group = self.config[template_type]
            if template_name not in template_group:
                available_templates = ", ".join(template_group.keys())
                raise ValueError(
                    f"Template '{template_name}' not found in {template_type}. "
                    f"Available templates: {available_templates}"
                )

            template_path = template_group[template_name]

            # Check if the template path is a nested structure (dict)
            if isinstance(template_path, dict):
                raise ValueError(
                    f"Template '{template_name}' in '{template_type}' is a nested structure. "
                    f"Direct access to nested templates is not supported."
                )

            return template_path
        except KeyError as e:
            logger.error(f"Invalid config structure: {e}")
            raise ValueError(f"Invalid config structure: missing key {e}") from e

    def init_template_structure(self) -> None:
        """Initialize template directory structure.

        Creates all necessary directories based on config.

        Raises
        ------
            ValueError: If any template path resolves outside base directory.
            KeyError: If config structure is invalid.

        """
        try:
            # Iterate through template types (e.g., project_templates, config_templates)
            for template_type, template_group in self.config.items():
                # Skip non-dict entries (like comments or metadata)
                if not isinstance(template_group, dict):
                    continue

                for template_name, relative_path in template_group.items():
                    if isinstance(relative_path, dict):
                        # Handle nested templates (like dev_templates)
                        for _, nested_path in relative_path.items():
                            full_path = self._resolve_template_path(nested_path)
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            logger.info(f"Created directory: {full_path.parent}")
                    else:
                        full_path = self._resolve_template_path(relative_path)
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created directory: {full_path.parent}")
        except KeyError as e:
            logger.error(f"Invalid config structure: {e}")
            raise ValueError(f"Invalid config structure: missing key {e}") from e
        except Exception as e:
            logger.error(f"Failed to initialize template structure: {e}")
            raise


class TemplateManager:
    """Manages template operations including copying and customization."""

    def __init__(self, resolver: TemplateResolver):
        """Initialize template manager.

        Args:
        ----
            resolver (TemplateResolver): Template resolver instance.

        """
        logger.debug("Initializing TemplateManager")
        self.resolver = resolver
