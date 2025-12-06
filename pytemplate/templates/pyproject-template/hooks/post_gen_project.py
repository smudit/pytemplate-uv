#!/usr/bin/env python
"""Post-generation hook to clean up optional files based on cookiecutter variables."""

import os
import shutil

# Get cookiecutter variables
include_github_actions = "{{ cookiecutter.include_github_actions }}"
mkdocs = "{{ cookiecutter.mkdocs }}"
codecov = "{{ cookiecutter.codecov }}"
dockerfile = "{{ cookiecutter.dockerfile }}"


def remove_file(filepath: str) -> None:
    """Remove a file if it exists."""
    if os.path.isfile(filepath):
        os.remove(filepath)
        print(f"Removed: {filepath}")


def remove_dir(dirpath: str) -> None:
    """Remove a directory and its contents if it exists."""
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
        print(f"Removed: {dirpath}")


def main() -> None:
    """Clean up optional files based on cookiecutter configuration."""
    # Remove GitHub Actions workflow if not enabled
    if include_github_actions != "y":
        remove_dir(".github")

    # Remove MkDocs files if not enabled
    if mkdocs != "y":
        remove_file("mkdocs.yml")
        remove_dir("docs")

    # Remove Codecov config if not enabled
    if codecov != "y":
        remove_file(".codecov.yml")

    # Remove Docker files if not enabled
    if dockerfile != "y":
        remove_file("Dockerfile")
        remove_file(".dockerignore")
        remove_file("docker-compose.yml")
        remove_dir(".devcontainer")


if __name__ == "__main__":
    main()
