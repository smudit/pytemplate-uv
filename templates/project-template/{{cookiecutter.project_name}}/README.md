# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Project Type

This is a {{ cookiecutter.project_type }} project.

## Requirements

- Python {{ cookiecutter.python_version }} or higher
{% if cookiecutter.project_type != "lib" %}
- Docker
{% endif %}

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

{% if cookiecutter.docker.docker_compose %}
## Running with Docker

```bash
docker-compose up
```

{% endif %}
## Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

{% if cookiecutter.project_type == "service" %}
## API Documentation

The API documentation is available at `/docs` when the service is running.

## Exposed Ports

{% for port in cookiecutter.service_ports.ports %}
- {{ port }}
{% endfor %}
{% endif %}