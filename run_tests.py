#!/usr/bin/env python3
"""Simple test runner script for pytemplate-uv tests."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite with proper error handling."""
    test_dir = Path("tests")
    if not test_dir.exists():
        print("Error: tests directory not found")
        return 1
    
    # List of test files to run
    test_files = [
        "tests/test_create_config.py",
        "tests/test_create_lib.py", 
        "tests/test_create_project_from_config.py",
        "tests/test_cli.py",
        "tests/test_template_manager.py",
        "tests/test_project_creator.py",
        "tests/test_edge_cases.py",
        "tests/test_config_validation.py"
    ]
    
    # Check which test files exist
    existing_files = []
    for test_file in test_files:
        if Path(test_file).exists():
            existing_files.append(test_file)
        else:
            print(f"Warning: {test_file} not found")
    
    if not existing_files:
        print("Error: No test files found")
        return 1
    
    print(f"Running tests for {len(existing_files)} test files...")
    
    # Try to run pytest
    try:
        cmd = [sys.executable, "-m", "pytest"] + existing_files + ["-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode
        
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
