# Project-Specific Development Guide - MyApp API

This guide contains project-specific conventions and overrides for the MyApp API project. LLM assistants should prioritize these instructions over global defaults.

## Project Overview

**Description**: RESTful API service for managing user workflows  
**Python Version**: 3.11+  
**Framework**: FastAPI with SQLAlchemy ORM  
**Database**: PostgreSQL with Alembic migrations

## Environment Setup

### Dependencies (`uv`)

```bash
# Initial setup
uv venv
source .venv/bin/activate
uv sync

# Run application
uv run uvicorn src.myapp.main:app --reload

# Run any command
uv run <command>
```

### Required Environment Variables

```bash
# .env file (copy from .env.example)
DATABASE_URL=postgresql://user:pass@localhost/myapp
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

## Project-Specific Structure

```
myapp-api/
├── src/
│   └── myapp/
│       ├── api/          # API endpoints
│       │   ├── v1/       # Version 1 endpoints
│       │   └── deps.py   # Shared dependencies
│       ├── core/         # Core functionality
│       │   ├── config.py # Settings with pydantic
│       │   └── security.py
│       ├── models/       # SQLAlchemy models
│       ├── schemas/      # Pydantic schemas
│       ├── services/     # Business logic
│       ├── db/          # Database utilities
│       └── main.py      # FastAPI app entry
├── tests/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Shared fixtures
├── alembic/            # Database migrations
├── scripts/            # Utility scripts
└── Makefile           # Common commands
```

## Development Commands

### Makefile Commands

```bash
make format      # Format with ruff
make lint        # Lint and auto-fix
make test        # Run all tests
make test-unit   # Run unit tests only
make migrate     # Run database migrations
make coverage    # Generate coverage report
make clean       # Clean cache files
```

### Database Operations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

## Coding Conventions

### API Endpoints

- **Versioning**: All endpoints under `/api/v1/`
- **Naming**: Use plural nouns (`/users`, `/products`)
- **HTTP Methods**: Follow REST conventions strictly
- **Response Models**: Always use Pydantic schemas

```python
@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Create a new user.
    
    Args:
        user: User creation data.
        db: Database session.
        current_user: Authenticated user.
    
    Returns:
        Created user data.
    
    Raises:
        HTTPException: If email already exists.
    """
```

### Database Models

- **Base Class**: Inherit from `Base` in `src/myapp/models/base.py`
- **Naming**: Singular class names, plural table names
- **Timestamps**: All models include `created_at`, `updated_at`
- **Soft Delete**: Use `deleted_at` field, never hard delete

### Service Layer

- **Location**: `src/myapp/services/`
- **Pattern**: One service class per domain entity
- **Dependency Injection**: Use FastAPI's `Depends()`
- **Error Handling**: Raise custom exceptions, handle in middleware

### Schemas

- **Request/Response**: Separate schemas for input/output
- **Validation**: Use Pydantic validators for business rules
- **Naming**: `{Entity}Create`, `{Entity}Update`, `{Entity}Response`

## Testing Requirements

### Test Coverage

- **Minimum**: 80% coverage required
- **Focus Areas**: Business logic, API endpoints, database operations
- **Excluded**: Migration files, config files

### Test Patterns

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService(db=Mock())
    
    async def test_create_user_success(self, user_service):
        # Arrange
        user_data = {"email": "test@example.com"}
        
        # Act
        result = await user_service.create(user_data)
        
        # Assert
        assert result.email == user_data["email"]
```

### Integration Tests

- **Database**: Use test database with transactions
- **API Tests**: Use `TestClient` from FastAPI
- **Fixtures**: Shared in `conftest.py`

## Configuration Management

### Settings (Dynaconf Alternative - Pydantic Settings)

```python
# src/myapp/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Logging

```python
# Use loguru for all logging
from loguru import logger

# Configure in main.py
logger.add("logs/app.log", rotation="1 day", retention="7 days")
logger.add(sys.stderr, level=settings.log_level)

# Usage
logger.info("Processing user request", user_id=user_id)
logger.error("Database connection failed", exc_info=True)
```

## API Documentation

- **Auto-generated**: Available at `/docs` (Swagger) and `/redoc`
- **Descriptions**: All endpoints must have docstrings
- **Examples**: Include request/response examples in schemas

## Deployment Considerations

- **Docker**: Multi-stage Dockerfile provided
- **Health Check**: Endpoint at `/health`
- **Metrics**: Prometheus metrics at `/metrics`
- **Migration**: Run migrations before starting app

## Security Requirements

- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Configured per endpoint
- **CORS**: Configured in `main.py` for allowed origins

## Performance Guidelines

- **Database Queries**: Use eager loading to avoid N+1
- **Caching**: Redis for session and frequently accessed data
- **Async**: All I/O operations must be async
- **Pagination**: Required for all list endpoints

## LLM Assistant Instructions

### Priority Tasks

1. **Always run tests** after making changes: `make test`
2. **Format and lint** before committing: `make format lint`
3. **Check migrations** when modifying models
4. **Update API docs** when changing endpoints

### Common Gotchas

- SQLAlchemy models need `__tablename__` explicitly set
- FastAPI dependencies must be yielded for proper cleanup
- Alembic migrations must be reviewed before applying
- Test database is cleared after each test run

### When Adding Features

1. Create Pydantic schema first
2. Add/modify SQLAlchemy model if needed
3. Implement service layer logic
4. Create API endpoint
5. Write comprehensive tests
6. Update API documentation

---
*Last Updated: 2024-01-15*  
*This file overrides global `CLAUDE.md` defaults where specified.*
