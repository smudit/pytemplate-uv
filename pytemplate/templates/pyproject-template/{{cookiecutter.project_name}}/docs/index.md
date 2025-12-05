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
from {{cookiecutter.package_name}} import main

# Get started with the package
main.hello()
```

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_name}}.git
cd {{cookiecutter.project_name}}
uv sync
```

Run tests:

```bash
make test
```

## License

This project is licensed under the {{cookiecutter.license}} License.
