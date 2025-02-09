FROM python:{{ cookiecutter.python_version }}-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install -r requirements.txt
COPY . .
CMD ["uv", "run", "src/main.py"]