FROM mcr.microsoft.com/devcontainers/python:{{cookiecutter.python_version}}

# Install uv package manager
RUN pip install --no-cache-dir uv

# Install pre-commit
RUN pip install --no-cache-dir pre-commit

# Set up workspace
WORKDIR /workspaces/{{cookiecutter.project_name}}

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (will be re-run by postCreateCommand for full sync)
RUN uv pip install --system -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user directories
RUN mkdir -p /home/vscode/.cache/uv
