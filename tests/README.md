# Tests for FileShare Pro

This directory contains all test files for the FileShare Pro application.

## Structure

```
tests/
├── __init__.py              # Makes this a Python package
├── conftest.py              # Shared pytest fixtures
├── test_app.py              # Tests for main application
├── test_auth.py             # Tests for authentication
├── test_file_operations.py  # Tests for file operations
├── test_api.py              # Tests for API endpoints
└── fixtures/                # Test data and fixtures
    ├── sample_files/        # Sample files for testing
    └── test_data.json       # Test data
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_app.py
```

Run specific test:
```bash
pytest tests/test_app.py::TestAuth::test_login
```

## Test Guidelines

- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies
- Test both success and failure scenarios
- Maintain good test coverage (aim for >80%)

## Fixtures

Common fixtures are defined in `conftest.py`:
- `app`: Flask test application
- `client`: Test client for HTTP requests
- `temp_dir`: Temporary directory for file operations
- `sample_user`: Mock user data
