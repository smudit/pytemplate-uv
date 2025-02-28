"""Template management module for handling template resolution and customization."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from .constants import (
    DEFAULT_USER_CONFIG_FILE,
    ENV_BASE_DIR,
    TEMPLATE_PATHS_FILE,
)
from .logger import logger

console = Console()


class TemplateResolver:
    """Handles template resolution and path management."""

    def _is_safe_path(self, path: Path, base_dir: Path) -> bool:
        """Validate that a path is safe (within base directory)."""
        try:
            return base_dir in path.resolve().parents
        except (RuntimeError, OSError):
            return False

    def _resolve_template_path(self, relative_path: str) -> Path:
        """Safely resolve template path relative to base directory."""
        try:
            # Normalize the path by resolving any relative components
            normalized_path = Path(relative_path).resolve()
            return normalized_path
        except FileNotFoundError:
            logger.error(f"Template path does not exist: {relative_path}")
            raise

    def __init__(self, config_path: str | None = None):
        """Initialize template resolver.

        Args:
        ----
            config_path (Optional[str]): Path to config file. If None, uses default locations.

        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.base_dir = self._get_base_dir()
        self.template_paths = self._load_template_paths()
        self.config = self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get default configuration path."""
        return DEFAULT_USER_CONFIG_FILE

    def _get_base_dir(self) -> Path:
        """Get base directory from environment variable or project root."""
        base_dir = os.environ.get(ENV_BASE_DIR)
        if base_dir:
            return Path(base_dir).resolve()

        # Use current working directory as default base directory
        return Path.cwd().resolve()

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
        if not self.config_path.exists():
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
        relative_path = self._get_relative_path(template_type, template_name)
        return self._resolve_template_path(relative_path)

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
            templates = self.config["template_paths"]["templates"]
            if template_type not in templates:
                available_types = ", ".join(templates.keys())
                raise ValueError(
                    f"Template type '{template_type}' not found. Available types: {available_types}"
                )

            template_group = templates[template_type]
            if template_name not in template_group:
                available_templates = ", ".join(template_group.keys())
                raise ValueError(
                    f"Template '{template_name}' not found in {template_type}. "
                    f"Available templates: {available_templates}"
                )

            return template_group[template_name]
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
            templates = self.config["template_paths"]["templates"]
            for template_type, template_group in templates.items():
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
        self.resolver = resolver

    def copy_templates(self, category: str | None = None) -> None:
        """Copy templates to local directory.

        Args:
        ----
            category (Optional[str]): Specific template category to copy.
                                    If None, copies all templates.

        """
        try:
            # First ensure directory structure exists
            self.resolver.init_template_structure()

            templates = self.resolver.config["template_paths"]["templates"]
            if category:
                if category not in templates:
                    raise ValueError(f"Template category '{category}' not found")
                self._copy_category(category, templates[category])
            else:
                # Copy all categories
                for cat_name, cat_templates in templates.items():
                    self._copy_category(cat_name, cat_templates)

        except Exception as e:
            logger.error(f"Failed to copy templates: {e}")
            raise

    def _copy_category(self, category: str, templates: dict[str, Any]) -> None:
        """Copy templates for a specific category.

        Args:
        ----
            category (str): Category name.
            templates (Dict[str, Any]): Template configuration for the category.

        """
        logger.info(f"Copying {category} templates...")

        for template_name, relative_path in templates.items():
            if isinstance(relative_path, dict):
                # Handle nested templates
                for nested_name, nested_path in relative_path.items():
                    self._copy_template(category, f"{template_name}/{nested_name}", nested_path)
            else:
                self._copy_template(category, template_name, relative_path)

    def _copy_template(self, category: str, template_name: str, relative_path: str) -> None:
        """Copy a single template.

        Args:
        ----
            category (str): Template category.
            template_name (str): Template name.
            relative_path (str): Relative path to the template.

        Raises:
        ------
            ValueError: If destination path is outside base directory.
            FileNotFoundError: If source template doesn't exist.
            OSError: If copy operation fails.

        """
        # Source is from configured base directory
        source_path = self.resolver.base_dir / relative_path
        if not source_path.exists():
            raise FileNotFoundError(
                f"Template source not found: {source_path}. Check base_dir: {self.resolver.base_dir}"
            )

        # Safely resolve destination path
        dest_path = self.resolver._resolve_template_path(relative_path)

        try:
            if source_path.is_dir():
                if dest_path.exists():
                    # Validate path before destructive operation
                    if not self.resolver._is_safe_path(dest_path, self.resolver.base_dir):
                        raise ValueError(f"Cannot delete directory outside base: {dest_path}")
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                if dest_path.exists():
                    # Validate path before destructive operation
                    if not self.resolver._is_safe_path(dest_path, self.resolver.base_dir):
                        raise ValueError(f"Cannot delete file outside base: {dest_path}")
                    dest_path.unlink()
                shutil.copy2(source_path, dest_path)

            logger.info(f"Copied {category}/{template_name} to {dest_path}")

        except (OSError, shutil.Error) as e:
            logger.error(f"Failed to copy template {template_name}: {e}")
            raise OSError(f"Failed to copy template {template_name}: {e}") from e
