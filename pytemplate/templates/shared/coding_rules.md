1. Linting
	•	Use Flake8 (Python) or ESLint (JavaScript) in every project.
	•	Run lint checks before committing code.

2. Formatting
	•	Always run Black (Python) or Prettier (JavaScript/TypeScript) on all files.
	•	Enforce consistent indentation, line length, and spacing rules.

3. Logging
	•	Use LogGuru exclusively for all logging.
	•	Store log files in the logs directory at the project root.
	•	Ensure log messages are clear and facilitate easy debugging
	•	Use appropriate log levels (trace, debug, info, success, warning, error, critical)
	•	Add context to logs where necessary (e.g., @logger.catch for error tracking)
	•	Configure log formatting for readability and consistency
	•	Use module name and function name in log messages

4. Type Hinting
	•	Provide explicit type hints for every function and method.
	•	Maintain consistency in type definitions across modules.
	•	Use `mypy` for static type checking (zero errors enforced).  
	•	Avoid `Any` unless strictly necessary.

5. Docstrings				
	•	Write concise docstrings for every class, function, and method.
	•	Follow a standardized format (e.g., Google-Style or reStructuredText).

6. Object-Oriented Coding
	•	Organize code into clear class structures.
	•	Avoid large monolithic files. Each class or related classes in separate files.

7. File Length Management
	•	Keep files below a reasonable limit (e.g., 500 lines).
	•	Split functionalities into logical modules.
	•	Use pathlib when handling file paths

8. Prefered libraries
	* Use pathlib when handling file paths

9. Additional Best Practices
	•	Write unit tests.
	•	Store secrets and configuration in environment variables, not in code.
	•	Avoid magic numbers, define constants with meaningful names.
    •	Use uv for dependency management and packaging.