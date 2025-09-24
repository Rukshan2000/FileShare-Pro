"""
Shared pytest fixtures for FileShare Pro tests.
"""
import os
import tempfile

import pytest

from app import app as flask_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the test database
    db_fd, flask_app.config["DATABASE"] = tempfile.mkstemp()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()

    with flask_app.app_context():
        yield flask_app

    # Clean up
    os.close(db_fd)
    os.unlink(flask_app.config["DATABASE"])


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup is handled by the system


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {"username": "testuser", "password": "testpass123", "role": "user"}


@pytest.fixture
def admin_user():
    """Sample admin user data for testing."""
    return {"username": "admin", "password": "admin123", "role": "admin"}


@pytest.fixture
def sample_file_data():
    """Sample file data for testing uploads."""
    return {
        "filename": "test.txt",
        "content": b"This is a test file content.",
        "mimetype": "text/plain",
    }
