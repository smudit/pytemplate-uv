from pathlib import Path

# These variables will be templated by cookiecutter
PROJECT_TYPE = "{{ cookiecutter.project_type }}"
DOCKER_COMPOSE = "{{ cookiecutter.docker.docker_compose }}" == "True"
DOCKER_IMAGE = "{{ cookiecutter.docker.docker_image }}" == "True"
PROJECT_NAME = "{{ cookiecutter.project_name }}"


def setup_project_structure():
    """Set up project structure based on project type."""
    # Create basic structure
    src_dir = Path("src")
    tests_dir = Path("tests")
    src_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    if PROJECT_TYPE == "lib":
        # Create library structure
        (src_dir / PROJECT_NAME).mkdir(parents=True, exist_ok=True)

    elif PROJECT_TYPE == "workspace":
        # Create workspace structure
        services_dir = Path("services")
        infra_dir = Path("infrastructure")
        services_dir.mkdir(exist_ok=True)
        infra_dir.mkdir(exist_ok=True)

    elif PROJECT_TYPE == "service":
        # Create service structure
        migrations_dir = Path("migrations")
        migrations_dir.mkdir(exist_ok=True)

    # Create __init__.py files
    for py_dir in src_dir.rglob("**/"):
        if py_dir.is_dir():
            (py_dir / "__init__.py").touch()
    (tests_dir / "__init__.py").touch()


def handle_conditional_files():
    """Handle conditional files based on project configuration."""
    # Handle docker-compose.yml
    if not DOCKER_COMPOSE:
        compose_file = Path("docker-compose.yml")
        if compose_file.exists():
            compose_file.unlink()

    # Handle Dockerfile
    if not DOCKER_IMAGE:
        dockerfile = Path("Dockerfile")
        if dockerfile.exists():
            dockerfile.unlink()


def cleanup_files():
    """Remove any temporary or unwanted files."""
    # Add any cleanup logic here if needed
    pass


def main():
    """Main post-generation hook."""
    setup_project_structure()
    handle_conditional_files()
    cleanup_files()


if __name__ == "__main__":
    main()
