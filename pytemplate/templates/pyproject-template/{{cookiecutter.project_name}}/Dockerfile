FROM python:{{cookiecutter.python_version}}-slim as builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy only the files needed for dependency installation
COPY pyproject.toml ./
COPY {{cookiecutter.package_name}} ./{{cookiecutter.package_name}}

# Use uv to install dependencies into system Python
RUN uv pip install --system .

FROM python:{{cookiecutter.python_version}}-slim

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy the installed dependencies from builder (use shell glob to handle version differences)
COPY --from=builder /usr/local/lib/python3*/site-packages /usr/local/lib/python3/site-packages
ENV PYTHONPATH=/usr/local/lib/python3/site-packages:/app

# Copy project files
COPY {{cookiecutter.package_name}} ./{{cookiecutter.package_name}}
COPY pyproject.toml ./

# Switch to non-root user
USER appuser

{% if cookiecutter.command_line_interface != "no" -%}
# Run the CLI application
CMD ["python", "-m", "{{cookiecutter.package_name}}.cli"]
{% else -%}
# Default entrypoint - customize as needed
CMD ["python", "-m", "{{cookiecutter.package_name}}"]
{% endif -%}
