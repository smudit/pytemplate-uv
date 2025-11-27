"""Tests for the main module."""

import importlib

import pytest


def test_module_imports():
    """Test that the main package can be imported."""
    module = importlib.import_module("{{cookiecutter.package_name}}")
    assert module is not None


def test_main_entry_point():
    """Test that the main module has expected entry points."""
    from {{cookiecutter.package_name}} import main

    # Main module should have __version__ or similar metadata
    assert hasattr(main, "__file__")


def test_config_loads():
    """Test that configuration can be loaded."""
    from {{cookiecutter.package_name}}.config import settings

    # Settings should be a Dynaconf instance
    assert settings is not None
    assert hasattr(settings, "get")


def test_logger_available():
    """Test that logger is available and configured."""
    from {{cookiecutter.package_name}}.logger import logger

    assert logger is not None
    # Logger should be callable
    logger.debug("Test log message")
