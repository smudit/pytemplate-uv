# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Installation

```bash
pip install {{cookiecutter.project_name}}
```

Or with uv:

```bash
uv add {{cookiecutter.project_name}}
```

## Quick Start

```python
from {{cookiecutter.package_name}}.logger import logger, setup_logger

# Configure logging (optional - reads from settings by default)
setup_logger()

# Use the logger
logger.info("Application started")
```

Or use the CLI:

```bash
{{cookiecutter.package_name}} --help
```

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_name}}.git
cd {{cookiecutter.project_name}}
task setup
```

Run tests:

```bash
task test
```

## License

This project is licensed under the {{cookiecutter.license}} License.
