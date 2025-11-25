---
allowed-tools: Task, Bash, Grep, Read, Edit, Write
argument-hint: [target] [--generate-missing]
description: Synchronize test coverage with code by generating missing tests
model: sonnet
---

# Test Sync Command

Synchronize test coverage with your codebase by generating missing test stubs, identifying untested code paths, and ensuring comprehensive coverage.

## Usage

```bash
/test-sync                      # Sync all tests
/test-sync --generate-missing   # Generate stubs for untested code
/test-sync path/to/module.py    # Sync specific module
```

## Instructions

You are a test coverage specialist. Your task is to ensure every function, class, and important code path has corresponding tests.

### Step 1: Identify Target Files

**If no target specified:**
1. Run `uv run pytest --cov=ms_ai_assistant --cov-report=term-missing` to get coverage report
2. Identify files with coverage < 80%
3. Prioritize files by:
   - Critical modules (core business logic)
   - Recently changed files (from git log)
   - Files with 0% coverage

**If target specified:**
- Use the provided file/directory path
- Validate it exists

### Step 2: Analyze Coverage Gaps

For each target file:

1. **Read the implementation file**
2. **Identify all testable units:**
   - Public functions (not starting with `_`)
   - Public methods in classes
   - Important private functions (complex logic)
   - Edge cases and error paths

3. **Check existing tests:**
   - Read corresponding test file if it exists
   - Identify which functions already have tests
   - Identify which functions are missing tests

4. **Analyze coverage report:**
   - Which lines are not covered?
   - Which branches are not tested?
   - Which edge cases are missing?

### Step 3: Generate Missing Test Stubs

For each untested function/method:

1. **Create test stub with proper structure:**

```python
def test_function_name_basic_functionality(self) -> None:
    """Test that function_name works with valid input."""
    # Arrange
    # TODO: Set up test data

    # Act
    # TODO: Call the function

    # Assert
    # TODO: Verify expected behavior
    pytest.skip("Test stub - implementation needed")
```

2. **Generate test cases for:**
   - ✅ Happy path (valid inputs)
   - ✅ Edge cases (empty input, max values, etc.)
   - ✅ Error cases (invalid input, exceptions)
   - ✅ Boundary conditions

3. **Include proper imports and fixtures:**
   - Import the function/class being tested
   - Add pytest decorators (@pytest.mark.asyncio, etc.)
   - Create fixtures if needed

### Step 4: Identify Missing Test Cases

For functions that HAVE tests but incomplete coverage:

1. **Analyze what's tested vs. what's not:**
   - Check if all code paths are covered
   - Check if all parameters are tested
   - Check if all return values are tested
   - Check if error conditions are tested

2. **Suggest additional test cases:**

```
## Additional Test Cases Needed

### test_existing_function.py
Currently tests:
- ✅ Basic functionality
- ✅ Valid input

Missing:
- ❌ Error handling for None input
- ❌ Edge case: empty list
- ❌ Async behavior verification
```

### Step 5: Handle --generate-missing Flag

If `--generate-missing` is provided:

1. **Create or update test files:**
   - If test file doesn't exist, create it with proper structure
   - If test file exists, append new test stubs
   - Use Write tool for new files, Edit tool for existing files

2. **Generate complete test structure:**

```python
"""
Tests for module_name.

This module tests [brief description].
"""

import pytest
from ms_ai_assistant.module_name import function_name


class TestFunctionName:
    """Tests for function_name function."""

    def test_function_name_with_valid_input(self) -> None:
        """Test function_name with valid input."""
        # Test implementation
        pytest.skip("Generated stub - needs implementation")

    def test_function_name_with_invalid_input(self) -> None:
        """Test function_name handles invalid input correctly."""
        pytest.skip("Generated stub - needs implementation")
```

3. **Add TODO comments for complex scenarios:**
   - Mark areas that need special attention
   - Note fixture requirements
   - Flag dependencies that need mocking

### Step 6: Update Fixtures

Identify if new fixtures are needed:

1. **Check conftest.py** for existing fixtures
2. **Suggest new fixtures** for common test data:
   - Database fixtures
   - Mock API responses
   - Sample data objects

3. **Generate fixture code** if requested:

```python
@pytest.fixture
def sample_user() -> dict:
    """Provide a sample user for testing."""
    return {
        "id": "user-123",
        "name": "Test User",
        "email": "test@example.com",
    }
```

### Step 7: Present Results

```
## Test Sync Results

### Coverage Analysis
- Current coverage: 24%
- Target coverage: 80%
- Gap: 56% (4,307 lines)

### Files Analyzed
1. ms_ai_assistant/module.py
   - Total functions: 15
   - Tested: 8 (53%)
   - Missing tests: 7

### Generated Test Stubs
✅ tests/test_module.py
   - Added test_function_a()
   - Added test_function_b()
   - Added test_function_c_error_handling()

### Existing Tests Needing Updates
⚠️  tests/test_module.py::test_existing_function
   - Missing edge case: empty input
   - Missing error case: None handling

### Next Steps
1. Implement generated test stubs (marked with pytest.skip)
2. Run `make test` to verify structure
3. Gradually implement tests to reach 80% coverage
4. Use `/test-update` to maintain tests as code changes
```

## Test Generation Patterns

### Pattern 1: Simple Function

```python
# Implementation
def calculate_sum(numbers: list[int]) -> int:
    return sum(numbers)

# Generated Tests
def test_calculate_sum_with_numbers(self) -> None:
    """Test calculate_sum with a list of numbers."""
    result = calculate_sum([1, 2, 3, 4, 5])
    assert result == 15

def test_calculate_sum_with_empty_list(self) -> None:
    """Test calculate_sum with an empty list."""
    result = calculate_sum([])
    assert result == 0
```

### Pattern 2: Async Function

```python
# Implementation
async def fetch_data(url: str) -> dict:
    # ... async implementation

# Generated Tests
@pytest.mark.asyncio
async def test_fetch_data_success(self) -> None:
    """Test fetch_data with valid URL."""
    # Mock HTTP request
    # Test implementation
    pytest.skip("Generated stub - needs implementation")
```

### Pattern 3: Class Methods

```python
# Implementation
class UserService:
    def create_user(self, data: dict) -> User:
        # ... implementation

# Generated Tests
class TestUserService:
    """Tests for UserService class."""

    @pytest.fixture
    def service(self) -> UserService:
        """Create UserService instance for testing."""
        return UserService()

    def test_create_user_with_valid_data(self, service: UserService) -> None:
        """Test create_user with valid user data."""
        pytest.skip("Generated stub - needs implementation")
```

## Coverage Priority Matrix

| Priority | Criteria | Action |
|----------|----------|--------|
| 🔴 Critical | Core business logic, 0% coverage | Generate tests immediately |
| 🟠 High | Public API, < 50% coverage | Generate comprehensive tests |
| 🟡 Medium | Support functions, < 80% coverage | Add missing edge cases |
| 🟢 Low | Utilities, > 80% coverage | Fine-tune existing tests |

## Safety Guidelines

1. **Don't overwrite existing tests**: Always use Edit to append, never Write to replace
2. **Match existing style**: Follow the project's test patterns and naming conventions
3. **Use pytest.skip**: Mark generated stubs so they don't cause false passes
4. **Group related tests**: Use test classes to organize related test cases
5. **Add docstrings**: Every generated test should have a clear description

## Integration Points

- **After new feature**: Run `/test-sync --generate-missing` for new modules
- **Before PR**: Ensure coverage is adequate with `/test-sync`
- **With /test-update**: Use /test-sync for new tests, /test-update for maintaining existing
- **With /test-cov**: Check coverage first with `/test-cov`, then sync with `/test-sync`

## File Structure Mapping

```
ms_ai_assistant/
├── module.py                → tests/test_module.py
├── package/
│   ├── __init__.py          → tests/package/test_init.py
│   └── submodule.py         → tests/test_submodule.py
└── chat_app/
    └── backend/
        └── api.py           → tests/test_api.py (or chat_app/tests/backend/test_api.py)
```

## Important Notes

- Use `uv run pytest` for all test operations
- Follow project's test structure (check existing tests/conftest.py)
- Use type hints in generated tests
- Add `@pytest.mark.asyncio` for async tests
- Import from the actual module being tested, not from __init__.py
- Generate tests that follow AAA pattern: Arrange, Act, Assert
- Use descriptive test names: `test_<function>_<scenario>_<expected>`
- Mark stubs with `pytest.skip("reason")` to avoid false passes

## Coverage Goals

- **Week 1**: 40% coverage (add tests for critical paths)
- **Week 2**: 50% coverage (add tests for public APIs)
- **Week 3**: 60% coverage (add edge case tests)
- **Week 4**: 70% coverage (add error handling tests)
- **Target**: 80% line coverage, 75% branch coverage
