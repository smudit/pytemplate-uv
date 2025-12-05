from __future__ import annotations

import os
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import typer
import yaml
from cookiecutter.main import cookiecutter

from .constants import TEMPLATE_PATHS_FILE
from .logger import logger
from .template_manager import TemplateResolver


def _validate_template(template: str, resolver: TemplateResolver) -> Path:
    """Validate and return the path to the specified template.

    Args:
    ----
        template (str): Name of the project template.
        resolver (TemplateResolver): Template resolver instance.

    Returns:
    -------
        Path: Path to the template directory.

    Raises:
    ------
        typer.BadParameter: If template is not found.

    """
    logger.debug(f"Validating template: {template}")
    try:
        template_path = resolver.get_template_path("project_scaffolds", template)
        logger.info(f"Using template path: {template_path}")

        # Check if the template path exists (skip for GitHub URLs)
        if str(template_path).startswith("gh:"):
            logger.debug("GitHub URL detected, skipping existence check")
            return template_path

        if not template_path.exists():
            # Try to find the template in the package directory
            package_dir = Path(__file__).parent

            # First try with the template name as is
            alternative_path = package_dir / "templates" / f"{template}-template"
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path

            # If that doesn't work, try with just the template name
            alternative_path = package_dir / "templates" / template
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path

            # If that still doesn't work, try with the full template path name
            template_name = template_path.name
            alternative_path = package_dir / "templates" / template_name
            if alternative_path.exists():
                logger.info(f"Using alternative template path: {alternative_path}")
                return alternative_path

            logger.error(f"Template path not found at: {template_path} or alternatives")
            raise ValueError(f"Template path not found: {template_path}")

        return template_path
    except ValueError as e:
        # Get available templates from config
        available_templates = list(resolver.config.get("project_scaffolds", {}).keys())

        error_msg = f"Template not found! Available templates: {', '.join(available_templates)}"
        logger.error(error_msg)
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(code=1) from e


def _get_context() -> dict[str, str]:
    """Retrieve context variables for project template.

    Returns
    -------
        A dictionary of context variables.

    """
    logger.debug("Retrieving context variables for project template")
    context = {
        "author": os.environ.get("USER", "your name"),
        "email": os.environ.get("USER_EMAIL", "your@email.com"),
        "github_username": os.environ.get("GITHUB_USERNAME", "your_username"),
    }
    logger.debug(f"Context variables: {context}")
    return context


def _create_project_with_cookiecutter(
    template_path: Path,
    context: dict,
    no_input: bool,
    overwrite: bool,
    template_resolver: TemplateResolver,
) -> str:
    logger.debug(f"Creating project with cookiecutter from template: {template_path}")

    try:
        if context.get("project", {}).get("type") == "lib":
            # Get the library template path from config (fpgmaas/cookiecutter-uv)
            lib_template = template_resolver.get_template_path("project_scaffolds", "pylibrary")
            dev_settings = context.get("development", {})
            docker_settings = context.get("docker", {})
            devcontainer_settings = context.get("devcontainer", {})

            # Helper to convert bool to "y"/"n" for cookiecutter
            def bool_to_yn(value: bool) -> str:
                return "y" if value else "n"

            # Map license names to cookiecutter-uv format
            license_mapping = {
                "MIT": "MIT license",
                "BSD": "BSD license",
                "ISC": "ISC license",
                "Apache 2.0": "Apache Software License 2.0",
                "GNU GPL v3": "GNU General Public License v3",
                "Not open source": "Not open source",
            }
            project_license = context["project"].get("license", "MIT")
            mapped_license = license_mapping.get(project_license, "MIT license")

            # Map type_checker to cookiecutter-uv format
            type_checker = dev_settings.get("type_checker", "mypy")
            if type_checker == "none":
                type_checker = "none"  # cookiecutter-uv accepts "none" to skip type checker

            # Build cookiecutter context for fpgmaas/cookiecutter-uv
            cookiecutter_context = {
                # Project settings
                "author": context["project"].get("author", "Your Name"),
                "email": context["project"].get("email", "your.email@example.com"),
                "author_github_handle": context["github"].get(
                    "github_username", "your-github-username"
                ),
                "project_name": context["project"]["name"].replace("_", "-"),
                "project_slug": context["project"]["name"].replace("-", "_"),
                "project_description": context["project"].get("description", "A Python library"),
                # Layout and structure
                "layout": dev_settings.get("layout", "src"),
                # CI/CD and tooling
                "include_github_actions": bool_to_yn(
                    dev_settings.get("include_github_actions", True)
                ),
                "publish_to_pypi": bool_to_yn(dev_settings.get("publish_to_pypi", True)),
                "deptry": bool_to_yn(dev_settings.get("deptry", True)),
                "mkdocs": bool_to_yn(dev_settings.get("mkdocs", True)),
                "codecov": bool_to_yn(dev_settings.get("codecov", True)),
                "dockerfile": bool_to_yn(docker_settings.get("docker_image", False)),
                "devcontainer": bool_to_yn(devcontainer_settings.get("enabled", False)),
                "type_checker": type_checker,
                "open_source_license": mapped_license,
            }

            return _execute_cookiecutter(lib_template, no_input, cookiecutter_context, overwrite)

        return _execute_cookiecutter(template_path, no_input, context, overwrite)
    except Exception as e:
        if "already exists" in str(e):
            logger.warning("Directory already exists")
            if typer.confirm(
                "\nDirectory already exists. Do you want to overwrite?", default=False
            ):
                logger.info("User confirmed overwrite, retrying...")
                if context.get("project", {}).get("type") == "lib":
                    return _execute_cookiecutter(lib_template, no_input, cookiecutter_context, True)
                return _execute_cookiecutter(template_path, no_input, context, True)
            else:
                logger.info("User chose not to overwrite. Exiting.")
                raise typer.Exit(1) from None
        raise


def _execute_cookiecutter(
    template_path: Path, no_input: bool, context: dict, overwrite: bool
) -> str:
    """Execute cookiecutter with consistent parameters."""
    return cookiecutter(
        str(template_path),
        no_input=no_input,
        extra_context=context,
        overwrite_if_exists=overwrite,
    )


class ProjectCreator:
    def __init__(self, config_path: str, interactive: bool = False):
        """Initialize a new instance of ProjectCreator.

        Args:
        ----
            config_path (str): Path to the YAML configuration file.
            interactive (bool, optional): If True, enable interactive mode (default is False).

        """
        logger.debug(
            f"Initializing ProjectCreator with config_path: {config_path}, "
            f"interactive: {interactive}"
        )
        self.config_path = Path(config_path)
        self.interactive = interactive
        self.config: dict[str, Any] = {}
        self.project_path: Path | None = None

        # Initialize template management
        self.template_resolver = TemplateResolver(str(TEMPLATE_PATHS_FILE))
        logger.debug("ProjectCreator initialization complete")

    def enable_testing_mode(self):
        """Enable testing mode to allow proper exception propagation for tests."""
        self._testing_mode = True

    def load_config(self) -> bool:
        """Load and validate configuration from YAML file.

        Returns
        -------
            bool: True if config was loaded and validated successfully, False otherwise.

        """
        logger.debug(f"Loading config from: {self.config_path}")
        try:
            self.config = yaml.safe_load(self.config_path.read_text())
            if self.config is None:
                self.config = {}
            logger.debug(f"Config loaded successfully with {len(self.config)} sections")
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {e}")
            # For CLI usage, raise typer.Exit, but for testing allow the original exception
            if hasattr(self, "_testing_mode") and self._testing_mode:
                raise
            raise typer.Exit(code=1) from e
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            # For CLI usage, raise typer.Exit, but for testing allow the original exception
            if hasattr(self, "_testing_mode") and self._testing_mode:
                raise
            raise typer.Exit(code=1) from e

        if not self.validate_config():
            logger.error("Invalid configuration")
            # For CLI usage, raise typer.Exit, but for testing allow KeyError for missing fields
            if hasattr(self, "_testing_mode") and self._testing_mode:
                # Check for missing required fields and raise KeyError for tests
                required_fields = ["project", "github", "docker", "devcontainer"]
                for field in required_fields:
                    if field not in self.config:
                        raise KeyError(f"Missing required field: {field}")
                # Check for missing project subfields
                if "project" in self.config:
                    project_required = ["type", "name"]
                    for field in project_required:
                        if field not in self.config["project"]:
                            raise KeyError(f"Missing required project field: {field}")
            raise typer.Exit(code=1)

        logger.info("Configuration loaded and validated successfully")
        return True

    def _validate_project_name(self) -> bool:
        """Validate the project name for allowed characters and length."""
        project_name = self.config["project"]["name"]
        logger.debug(f"Validating project name: {project_name}")

        # Check length
        if len(project_name) < 1 or len(project_name) > 100:
            logger.error("Project name must be between 1 and 100 characters")
            return False

        # Check for valid characters (letters, numbers, underscore, hyphen)
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            logger.error("Project name can only contain letters, numbers, underscores, and hyphens")
            return False

        logger.debug("Project name validation successful")
        return True

    def _validate_development_settings(self) -> bool:
        """Validate development settings."""
        dev_settings = self.config.get("development", {})
        project_type = self.config["project"]["type"]

        # Validate layout option for library projects (cookiecutter-uv)
        if project_type == "lib":
            layout = dev_settings.get("layout", "src")
            valid_layouts = ["src", "flat"]
            if layout not in valid_layouts:
                logger.error(f"Invalid layout option: {layout}")
                logger.error(f"Valid options are: {', '.join(valid_layouts)}")
                return False

            type_checker = dev_settings.get("type_checker", "mypy")
            valid_type_checkers = ["mypy", "none"]
            if type_checker not in valid_type_checkers:
                logger.error(f"Invalid type_checker option: {type_checker}")
                logger.error(f"Valid options are: {', '.join(valid_type_checkers)}")
                return False

        return True

    def validate_config(self) -> bool:
        """Validate the configuration structure."""
        logger.debug("Starting configuration validation")
        if not self._validate_required_sections():
            return False

        if not self._validate_project_type():
            return False

        if not self._validate_docker_settings():
            return False

        if not self._validate_project_name():
            return False

        if not self._validate_development_settings():
            return False

        logger.debug("Configuration validation completed successfully")
        return True

    def _validate_required_sections(self) -> bool:
        required_sections = ["project", "github", "docker", "devcontainer"]
        logger.debug(f"Validating required sections: {required_sections}")
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required section: {section}")
                return False

        # AI configuration is now loaded from template_paths.yaml, not from project config
        # No need to add AI section to project config

        logger.debug("Required sections validation successful")
        return True

    def _validate_project_type(self) -> bool:
        project_type = self.config["project"]["type"]
        logger.debug(f"Validating project type: {project_type}")
        if project_type not in ["lib", "workspace", "service"]:
            logger.error("Invalid project type")
            return False
        logger.debug("Project type validation successful")
        return True

    def _validate_docker_settings(self) -> bool:
        project_type = self.config["project"]["type"]
        logger.debug(f"Validating Docker settings for project type: {project_type}")

        # Get docker config with defaults
        docker_config = self.config.get("docker", {})
        docker_image = docker_config.get("docker_image", False)

        # Libraries can optionally have Docker (supported by cookiecutter-uv)
        # Services must have Docker
        if project_type == "service" and not docker_image:
            logger.error("Service projects require Docker image configuration")
            return False
        logger.debug("Docker settings validation successful")
        return True

    def create_project_from_config(self, force: bool = False) -> bool:
        """Create and initialize project addons like docker, devcontainer etc."""
        logger.info("Starting project creation from configuration")
        try:
            # Load and validate config first
            self.load_config()

            project_type = self.config["project"]["type"]
            project_name = self.config["project"]["name"]
            logger.info(f"Creating {project_type} project: {project_name}")

            # For library projects, use the pylibrary template
            if project_type == "lib":
                logger.info("Creating library project structure...")
                template_path = _validate_template("pylibrary", self.template_resolver)
                context = {
                    "project_name": project_name,
                    **_get_context(),
                    **self.config,  # Include all config settings
                }

                output_dir = _create_project_with_cookiecutter(
                    template_path, context, not self.interactive, force, self.template_resolver
                )

                self.project_path = Path(output_dir)
                logger.info(f"Created Python package structure at: {self.project_path}")

                # Always initialize local git repository
                if not self.initialize_local_git_repo():
                    logger.error("Failed to initialize local git repository")
                    return False

                # Create GitHub repo if requested
                if self.config["github"]["add_on_github"]:
                    logger.info("GitHub repository creation requested")
                    if not self.create_github_repo():
                        return False

                # Replace Makefile with Taskfile for lib projects
                if not self._setup_taskfile_for_lib():
                    logger.warning("Failed to set up Taskfile for lib project")

                # Set up .envrc for lib projects (add to project and .gitignore)
                if not self._setup_envrc():
                    logger.warning("Failed to set up .envrc for lib project")

                # Copy AI copilot templates for lib projects
                copilots = self._get_copilots_config()
                if copilots:
                    logger.info(f"Found {len(copilots)} AI copilot configurations")
                    if not self.copy_ai_templates():
                        return False

                logger.info(f"Project created successfully at {self.project_path}")
                return True

            # For non-lib project types (service, workspace), add project structure and addons
            # Get development settings with defaults
            dev_settings = self.config.get("development", {})

            # Helper to convert bool to "y"/"n" for cookiecutter
            def bool_to_yn(value: bool, default: bool = True) -> str:
                return "y" if value else "n"

            # Extract primary port from service_ports config
            service_ports_config = self.config.get("service_ports", {"ports": [8000]})
            ports_list = service_ports_config.get("ports", [8000])
            primary_port = ports_list[0] if ports_list else 8000

            context = {
                "project_name": project_name,
                "project_type": project_type,
                "description": self.config["project"].get("description", ""),
                "author": self.config["project"].get("author", ""),
                "email": self.config["project"].get("email", ""),
                "version": self.config.get("version", "0.1.0"),
                "python_version": self.config["project"].get("python_version", "3.11"),
                "github": self.config["github"],
                "github_username": self.config["github"].get("github_username", ""),
                "docker": self.config["docker"],
                "devcontainer": self.config["devcontainer"],
                "service_ports": service_ports_config,
                "primary_port": str(primary_port),
                # Development settings mapped to cookiecutter variables
                "mypy": bool_to_yn(dev_settings.get("use_mypy", True)),
                "coverage": bool_to_yn(dev_settings.get("use_pytest", True)),
                "dockerfile": bool_to_yn(self.config.get("docker", {}).get("docker_image", True)),
                "license": self.config["project"].get("license", "MIT"),
                "envfile": dev_settings.get("envfile", ".env"),
                # New toolchain options
                "deptry": bool_to_yn(dev_settings.get("deptry", True)),
                "codecov": bool_to_yn(dev_settings.get("codecov", True)),
                "mkdocs": bool_to_yn(dev_settings.get("mkdocs", True)),
                "include_github_actions": bool_to_yn(
                    dev_settings.get("include_github_actions", True)
                ),
            }
            logger.debug(f"Project context: {context}")

            # Get template path for addons and validate it
            template_path = _validate_template("pyproject", self.template_resolver)

            # Add non-package addons using cookiecutter
            output_dir = _create_project_with_cookiecutter(
                template_path, context, not self.interactive, force, self.template_resolver
            )

            self.project_path = Path(output_dir)

            # Always initialize local git repository
            if not self.initialize_local_git_repo():
                logger.error("Failed to initialize local git repository")
                return False

            # Create GitHub repository if requested
            if self.config.get("github", {}).get("add_on_github"):
                logger.info("GitHub repository creation requested")
                if not self.create_github_repo():
                    return False
            # Always check for AI copilots from template_paths.yaml
            copilots = self._get_copilots_config()
            if copilots:
                logger.info(f"Found {len(copilots)} AI copilot configurations")
                if not self.copy_ai_templates():
                    return False
            logger.info(f"Project created successfully at {self.project_path}")
            return True

        except Exception as e:
            logger.exception(f"Failed to create project: {str(e)}")
            # Re-raise in testing mode for proper exception propagation
            if hasattr(self, "_testing_mode") and self._testing_mode:
                raise
            return False

    def initialize_local_git_repo(self) -> bool:
        """Initialize a local git repository with main branch.

        Returns
        -------
            bool: True if successful, False otherwise

        """
        if not self.project_path:
            logger.error("Project path not set")
            return False

        if not (self.project_path / ".git").exists():
            logger.info("Initializing local git repository with main branch...")
            current_dir = os.getcwd()
            try:
                os.chdir(self.project_path)

                # Initialize git repo - try new syntax first, fall back for older git
                use_fallback = False
                try:
                    # Try Git >= 2.28 syntax: git init -b main
                    subprocess.check_call(
                        ["git", "init", "-b", "main"],
                        stderr=subprocess.DEVNULL,
                    )
                except subprocess.CalledProcessError:
                    # Git < 2.28: init with default branch, rename after commit
                    use_fallback = True
                    subprocess.check_call(["git", "init"])

                subprocess.check_call(["git", "add", "."])
                subprocess.check_call(["git", "commit", "-m", "Initial commit"])

                # For older Git: rename branch to main after commit (avoids broken state)
                if use_fallback:
                    subprocess.check_call(["git", "branch", "-M", "main"])

                logger.info("Local git repository initialized successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to initialize git repository: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error during git initialization: {e}")
                return False
            finally:
                os.chdir(current_dir)
        else:
            logger.info("Git repository already exists")
            return True

    def create_github_repo(self) -> bool:
        """Create a GitHub repository using the GitHub CLI (gh) command.

        Reads the github configuration to determine if the repository should be private.
        Changes to the project directory before running the command and changes back after.
        """

        @contextmanager
        def change_directory(path: Path):
            current_dir = os.getcwd()
            os.chdir(path)
            try:
                yield
            finally:
                os.chdir(current_dir)

        logger.info("Starting GitHub repository creation")
        if not self.project_path:
            logger.error("Project path not set")
            return False

        github_config = self.config.get("github", {})
        repo_name = github_config.get("repo_name", "")
        logger.debug(f"Repository name: {repo_name}")

        if not re.fullmatch(r"^[a-z0-9-_]{1,100}$", repo_name.lower()):
            raise ValueError(
                f"Invalid repository name: {repo_name} - must be 1-100 chars a-z, 0-9, -, _"
            )
        is_private = github_config.get("repo_private", False)
        private_flag = "--private" if is_private else "--public"

        # Get description from project config
        description = self.config.get("project", {}).get("description", "")
        logger.debug(f"Repository visibility: {'private' if is_private else 'public'}")
        logger.debug(f"Repository description: {description}")

        try:
            # Initialize local git repo first
            if not self.initialize_local_git_repo():
                logger.error("Failed to initialize local git repository")
                return False

            with change_directory(self.project_path):
                logger.info(f"Changed to project directory: {self.project_path}")

                cmd = ["gh", "repo", "create", repo_name, private_flag, "--source=.", "--push"]

                # Add description if provided
                if description:
                    cmd.extend(["--description", description])

                logger.info(f"Running GitHub command: {' '.join(cmd)}")

                subprocess.check_call(cmd)
                logger.info("GitHub repository created and code pushed successfully")
                return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run GitHub command: {e}")
            return False
        except subprocess.TimeoutExpired as e:
            logger.error(f"GitHub command timed out: {e}")
            return False

    def _get_copilots_config(self) -> dict[str, str]:
        """Load copilots configuration from template_paths.yaml.

        Returns
        -------
            dict[str, str]: Dictionary mapping copilot names to their rules file paths.

        """
        # Load from template_paths.yaml instead of project config
        copilots_config = self.template_resolver.config.get("ai_copilots", {})

        if not isinstance(copilots_config, dict):
            logger.warning(
                f"AI copilots configuration is not a dict, found {type(copilots_config).__name__}"
            )
            return {}

        logger.debug(f"Loaded {len(copilots_config)} AI copilot configurations")
        return copilots_config

    def _load_template_content(self, template_type: str, template_name: str) -> str | None:
        """Load content from a template file.

        Args:
        ----
            template_type: Type of template (e.g., "shared_resources").
            template_name: Name of the template (e.g., "coding_rules").

        Returns:
        -------
            str | None: Template content if found, None otherwise.

        """
        try:
            template_path = self.template_resolver.get_template_path(template_type, template_name)
            logger.debug(f"Found {template_name} template at: {template_path}")

            if not template_path.exists():
                logger.warning(f"{template_name} template not found at {template_path}")
                return None

            return template_path.read_text()
        except (ValueError, FileNotFoundError) as e:
            logger.warning(f"Could not find {template_name} template: {e}")
            return None

    def _copy_rules_to_path(self, rules_content: str, target_path: str) -> bool:
        """Copy rules content to a specific path.

        Args:
        ----
            rules_content: Content to write.
            target_path: Relative path within project directory.

        Returns:
        -------
            bool: True if successful, False otherwise.

        """
        if self.project_path is None:
            logger.error("Project path is not set")
            return False

        try:
            full_path = self.project_path / target_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(rules_content)
            logger.info(f"Copied coding rules to {target_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy rules to {target_path}: {e}")
            return False

    def _setup_taskfile_for_lib(self) -> bool:
        """Set up Taskfile for lib projects by copying template and removing Makefile.

        Returns
        -------
            bool: True if successful, False otherwise.

        """
        if self.project_path is None:
            logger.error("Project path is not set")
            return False

        try:
            # Load Taskfile template for lib projects
            taskfile_content = self._load_template_content("shared_resources", "taskfile_lib")
            if not taskfile_content:
                logger.warning("Taskfile template for lib not found")
                return False

            # Write Taskfile.yaml to project
            taskfile_path = self.project_path / "Taskfile.yaml"
            taskfile_path.write_text(taskfile_content)
            logger.info("Created Taskfile.yaml for lib project")

            # Remove Makefile if it exists (generated by cookiecutter-uv)
            makefile_path = self.project_path / "Makefile"
            if makefile_path.exists():
                makefile_path.unlink()
                logger.info("Removed Makefile (replaced by Taskfile)")

            return True
        except Exception as e:
            logger.error(f"Failed to set up Taskfile for lib project: {e}")
            return False

    def _setup_envrc(self) -> bool:
        """Set up .envrc file and add it to .gitignore.

        Returns
        -------
            bool: True if successful, False otherwise.

        """
        if self.project_path is None:
            logger.error("Project path is not set")
            return False

        try:
            # Load .envrc template from shared resources
            envrc_content = self._load_template_content("shared_resources", "envrc")
            if not envrc_content:
                logger.warning(".envrc template not found")
                return False

            # Write .envrc to project root
            envrc_path = self.project_path / ".envrc"
            envrc_path.write_text(envrc_content)
            logger.info("Created .envrc file")

            # Add .envrc to .gitignore if not already present
            gitignore_path = self.project_path / ".gitignore"
            if gitignore_path.exists():
                gitignore_content = gitignore_path.read_text()
                if ".envrc" not in gitignore_content:
                    # Add .envrc to .gitignore
                    with gitignore_path.open("a") as f:
                        f.write("\n# direnv\n.envrc\n")
                    logger.info("Added .envrc to .gitignore")
            else:
                # Create .gitignore with .envrc
                gitignore_path.write_text("# direnv\n.envrc\n")
                logger.info("Created .gitignore with .envrc")

            return True
        except Exception as e:
            logger.error(f"Failed to set up .envrc: {e}")
            return False

    def copy_ai_templates(self) -> bool:
        """Copy AI-related template files based on configuration.

        Returns
        -------
            bool: True if copy operation was successful, False otherwise.

        """
        logger.info("Starting AI template copy operation")
        if not self.project_path:
            logger.error("Project path not set")
            return False

        try:
            copilots_config = self._get_copilots_config()
            if not copilots_config:
                logger.debug("No AI copilot configuration found, skipping template copy")
                return True

            # Load template content
            rules_content = self._load_template_content("shared_resources", "coding_rules")
            if not rules_content:
                logger.warning("Coding rules template not found, skipping AI rules creation")
                return True

            # Copy rules for each configured copilot
            success = True
            for copilot_name, rules_path in copilots_config.items():
                logger.debug(f"Processing copilot '{copilot_name}' with path '{rules_path}'")
                if not self._copy_rules_to_path(rules_content, rules_path):
                    success = False

            logger.info("AI template copy operation completed")
            return success

        except Exception as e:
            logger.error(f"Failed to copy AI templates: {e}")
            return False
