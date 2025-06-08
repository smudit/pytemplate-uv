"""Pytest configuration and fixtures for pytemplate-uv."""

import logging
import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
import yaml
from loguru import logger


class PropagateHandler(logging.Handler):
    """A handler that routes Loguru messages to Python's standard logging."""

    def emit(self, record):
        # Use whatever logger name you want. Typically, Loguru logs have `record.name == 'loguru'`.
        logging.getLogger(record.name).handle(record)


# hook into pytest to propagate Loguru logs to Python's logging so that caplog can capture them
@pytest.fixture(scope="session", autouse=True)
def _setup_loguru_to_python_logging():
    """Propagate Loguru logs to Python's logging so that caplog can capture them."""
    # Remove any default Loguru sinks to avoid double or extra output
    logger.remove()

    # Add our custom handler
    logger.add(PropagateHandler(), level="DEBUG")  # or "INFO", "ERROR", etc.

    # Optionally configure the root logger level, etc.
    logging.basicConfig(level=logging.DEBUG)

    yield  # tests run here

    # (Optional) remove the custom sink after tests
    logger.remove()


@pytest.fixture
def temp_project_dir() -> str:
    """Create a temporary directory for project creation.

    Returns
    -------
        str: Path to the temporary directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)


@pytest.fixture
def project_templates_path() -> Path:
    """Get the path to project templates.

    Returns
    -------
        Path: Path to the templates directory

    """
    return Path(__file__).parent.parent / "templates"


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for configuration files.

    Yields
    ------
        Path: Path to temporary config directory

    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        yield temp_dir


@pytest.fixture
def sample_lib_config(temp_config_dir: Path) -> Path:
    """Create a sample library configuration file.

    Args:
    ----
        temp_config_dir: Temporary directory for config files

    Returns:
    -------
        Path: Path to the sample config file

    """
    config = {
        "project": {
            "type": "lib",
            "name": "test-lib",
            "description": "Test library project",
            "python_version": "3.9",
        },
        "github": {"add_on_github": False, "repo_name": "test-lib", "repo_private": False},
        "docker": {"docker_image": False, "docker_compose": False},
        "devcontainer": {"enabled": False},
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
    }

    config_path = temp_config_dir / "lib_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture
def temp_templates_dir(temp_config_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary templates directory with basic structure.

    Args:
    ----
        temp_config_dir: Temporary directory for templates

    Yields:
    ------
        Path: Path to temporary templates directory

    """
    templates_dir = temp_config_dir / "templates"
    templates_dir.mkdir()

    # Create basic template structure
    (templates_dir / "pyproject-template").mkdir()
    (templates_dir / "fastapi-template").mkdir()
    (templates_dir / "shared").mkdir()

    # Create shared coding rules template
    (templates_dir / "shared" / "coding_rules.md").write_text("""
    # Coding Rules for Tests
    1. Use type hints
    2. Write unit tests
    3. Follow PEP8
    """)

    # Create mock template files instead of using actual cookiecutter templates
    pyproject_dir = templates_dir / "pyproject-template"
    (pyproject_dir / "cookiecutter.json").write_text("""
    {
        "project_name": "test-pyproject",
        "package_name": "test_pyproject",
        "description": "Test PyProject",
        "author": "Test Author",
        "envfile": ".env"
    }
    """)

    # Create the {{cookiecutter.project_name}} directory structure
    cookie_project_dir = pyproject_dir / "{{cookiecutter.project_name}}"
    cookie_project_dir.mkdir(parents=True)

    # Create basic project structure
    (cookie_project_dir / "pyproject.toml").write_text("""
    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "{{cookiecutter.project_name}}"
    version = "0.1.0"
    """)

    # Create package directory
    package_dir = cookie_project_dir / "{{cookiecutter.package_name}}"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("")
    (package_dir / "main.py").write_text("""def main():
        print("Hello from {{cookiecutter.project_name}}")
    """)

    # Create tests directory
    test_dir = cookie_project_dir / "tests"
    test_dir.mkdir(parents=True)
    (test_dir / "__init__.py").write_text("")
    (test_dir / "test_main.py").write_text("""def test_placeholder():
        assert True
    """)

    fastapi_dir = templates_dir / "fastapi-template"
    (fastapi_dir / "cookiecutter.json").write_text("""
    {
        "project_name": "test-fastapi",
        "package_name": "test_fastapi",
        "description": "Test FastAPI Project",
        "author": "Test Author",
        "envfile": ".env"
    }
    """)

    # Create the {{cookiecutter.project_name}} directory structure for FastAPI
    fastapi_cookie_dir = fastapi_dir / "{{cookiecutter.project_name}}"
    fastapi_cookie_dir.mkdir(parents=True)

    # Create basic FastAPI project structure
    (fastapi_cookie_dir / "pyproject.toml").write_text("""
    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "{{cookiecutter.project_name}}"
    version = "0.1.0"
    
    [dependencies]
    fastapi = "^0.95.0"
    """)

    # Create package directory for FastAPI
    fastapi_package_dir = fastapi_cookie_dir / "{{cookiecutter.package_name}}"
    fastapi_package_dir.mkdir(parents=True)
    (fastapi_package_dir / "__init__.py").write_text("")
    (fastapi_package_dir / "main.py").write_text("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
    """)

    # Create tests directory for FastAPI
    fastapi_test_dir = fastapi_cookie_dir / "tests"
    fastapi_test_dir.mkdir(parents=True)
    (fastapi_test_dir / "__init__.py").write_text("")
    (fastapi_test_dir / "test_api.py").write_text("""def test_placeholder():
        assert True
    """)

    yield templates_dir

    # Cleanup
    if templates_dir.exists():
        shutil.rmtree(templates_dir)


@pytest.fixture
def mock_template_config(temp_templates_dir: Path) -> Path:
    """Create a mock template configuration file.

    Args:
    ----
        temp_templates_dir: Temporary templates directory

    Returns:
    -------
        Path: Path to the mock config file

    """
    # Create the configs directory and template files
    configs_dir = temp_templates_dir / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Create mock config template files
    for project_type in ["lib", "service", "workspace"]:
        template_file = configs_dir / f"{project_type}.yaml.template"
        template_content = f"""
project:
  type: {project_type}
  name: test-{project_type}
  description: Test {project_type} project
  author: Test Author
  email: test@example.com
github:
  add_on_github: false
  repo_name: test-{project_type}
  repo_private: false
docker:
  docker_image: {str(project_type == "service").lower()}
  docker_compose: false
devcontainer:
  enabled: false
ai:
  copilots: {{}}
"""
        template_file.write_text(template_content)

    # Use the actual structure from template_paths.yaml
    config = {
        "project_templates": {
            "pyproject": str(temp_templates_dir / "pyproject-template"),
            "pylibrary": str(
                temp_templates_dir / "pyproject-template"
            ),  # Use local template for testing
        },
        "config_templates": {
            "lib": str(configs_dir / "lib.yaml.template"),
            "service": str(configs_dir / "service.yaml.template"),
            "workspace": str(configs_dir / "workspace.yaml.template"),
        },
        "shared": str(temp_templates_dir / "shared"),
    }

    config_path = temp_templates_dir / "template_paths.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture(autouse=True)
def setup_environment(temp_project_dir: str, mock_template_config: Path, monkeypatch) -> None:
    """Set up environment variables for testing.

    Args:
    ----
        temp_project_dir: Temporary directory for project
        mock_template_config: Path to mock template config
        monkeypatch: pytest monkeypatch fixture

    """
    os.environ["TEMPLATE_CONFIG_PATH"] = str(mock_template_config)
    os.environ["PROJECT_BASE_DIR"] = temp_project_dir

    # Mock the TEMPLATE_PATHS_FILE constant to use our mock config
    monkeypatch.setattr("pytemplate.constants.TEMPLATE_PATHS_FILE", mock_template_config)
    monkeypatch.setattr("pytemplate.template_manager.TEMPLATE_PATHS_FILE", mock_template_config)
    monkeypatch.setattr("pytemplate.project_creator.TEMPLATE_PATHS_FILE", mock_template_config)


@pytest.fixture(autouse=True)
def mock_cookiecutter(monkeypatch):
    """Mock cookiecutter function for testing."""

    def mock_cookie(*args, **kwargs):
        """Create a simple directory structure for testing."""
        output_dir = kwargs.get("output_dir", ".")
        project_name = kwargs.get("extra_context", {}).get("project_name", "test-project")
        extra_context = kwargs.get("extra_context", {})

        # Create output directory
        project_path = Path(output_dir) / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Create basic project structure
        (project_path / "pyproject.toml").write_text(
            f'[project]\nname = "{project_name}"\nversion = "0.1.0"\n'
        )

        # Create README.md file
        (project_path / "README.md").write_text(
            f"# {project_name}\n\n{extra_context.get('description', 'A Python project')}\n"
        )

        # Create package directory with the same name
        package_name = project_name.replace("-", "_")
        package_path = project_path / "src" / package_name
        package_path.mkdir(parents=True, exist_ok=True)
        (package_path / "__init__.py").write_text("")
        (package_path / "main.py").write_text("def main():\n    print('Hello World')\n")

        # Create tests directory
        test_path = project_path / "tests"
        test_path.mkdir(parents=True, exist_ok=True)
        (test_path / "__init__.py").write_text("")
        (test_path / "test_main.py").write_text("def test_main():\n    assert True\n")

        # Create docs directory if sphinx is enabled
        development_config = extra_context.get("development", {})
        if extra_context.get("sphinx_docs") == "yes" or (
            isinstance(development_config, dict) and development_config.get("use_sphinx")
        ):
            docs_path = project_path / "docs"
            docs_path.mkdir(parents=True, exist_ok=True)
            (docs_path / "conf.py").write_text("")
            (docs_path / "index.rst").write_text("Welcome to documentation")

        # Create CLI file if CLI is enabled
        cli_interface = extra_context.get("command_line_interface")
        if cli_interface and cli_interface != "no":
            cli_path = package_path / "cli.py"
            cli_path.write_text("import click\n\n@click.group()\ndef cli():\n    pass\n")
        elif isinstance(development_config, dict):
            dev_cli = development_config.get("command_line_interface", "no")
            if dev_cli and dev_cli != "no":
                cli_path = package_path / "cli.py"
                cli_path.write_text("import click\n\n@click.group()\ndef cli():\n    pass\n")

        # Create Docker files if docker is enabled
        docker_config = extra_context.get("docker", {})
        if isinstance(docker_config, dict):
            if docker_config.get("docker_image"):
                (project_path / "Dockerfile").write_text(
                    "FROM python:3.11-slim\nWORKDIR /app\nCOPY . .\nRUN pip install .\nCMD ['python', '-m', 'package']\n"
                )
            if docker_config.get("docker_compose"):
                (project_path / "docker-compose.yml").write_text(
                    "version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - '8000:8000'\n"
                )

        # Create devcontainer files if enabled
        devcontainer_config = extra_context.get("devcontainer", {})
        if isinstance(devcontainer_config, dict) and devcontainer_config.get("enabled"):
            devcontainer_dir = project_path / ".devcontainer"
            devcontainer_dir.mkdir(parents=True, exist_ok=True)
            (devcontainer_dir / "devcontainer.json").write_text(
                '{\n  "name": "Python 3",\n  "image": "mcr.microsoft.com/devcontainers/python:3.11"\n}\n'
            )

        return str(project_path)

    # Replace cookiecutter with our mock version
    monkeypatch.setattr("pytemplate.project_creator.cookiecutter", mock_cookie)


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess calls for testing GitHub integration."""

    def mock_check_call(*args, **kwargs):
        """Mock subprocess.check_call."""
        return 0

    def mock_run(*args, **kwargs):
        """Mock subprocess.run."""
        from subprocess import CompletedProcess

        return CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.check_call", mock_check_call)
    monkeypatch.setattr("subprocess.run", mock_run)


@pytest.fixture
def sample_service_config(temp_config_dir: Path) -> Path:
    """Create a sample service configuration file.

    Args:
    ----
        temp_config_dir: Temporary directory for config files

    Returns:
    -------
        Path: Path to the sample config file

    """
    config = {
        "project": {
            "type": "service",
            "name": "test-service",
            "description": "Test service project",
            "python_version": "3.11",
            "author": "Test Author",
            "email": "test@example.com",
        },
        "github": {"add_on_github": True, "repo_name": "test-service", "repo_private": False},
        "docker": {"docker_image": True, "docker_compose": True},
        "devcontainer": {"enabled": True},
        "service_ports": {"ports": ["8000", "8080"]},
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
    }

    config_path = temp_config_dir / "service_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


@pytest.fixture
def sample_workspace_config(temp_config_dir: Path) -> Path:
    """Create a sample workspace configuration file.

    Args:
    ----
        temp_config_dir: Temporary directory for config files

    Returns:
    -------
        Path: Path to the sample config file

    """
    config = {
        "project": {
            "type": "workspace",
            "name": "test-workspace",
            "description": "Test workspace project",
            "python_version": "3.11",
            "author": "Test Author",
            "email": "test@example.com",
        },
        "github": {"add_on_github": True, "repo_name": "test-workspace", "repo_private": False},
        "docker": {"docker_image": False, "docker_compose": False},
        "devcontainer": {"enabled": True},
        "ai": {
            "copilots": {
                "cursor_rules_path": ".cursor/rules/coding_rules.md",
                "cline_rules_path": ".clinerules",
            }
        },
    }

    config_path = temp_config_dir / "workspace_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path
