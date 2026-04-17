"""
Pytest configuration - this must be loaded before app.py imports database.
"""

import pytest
import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# CRITICAL: Set test database path BEFORE any imports from node_manager
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.close(_test_db_fd)
os.environ["DATABASE_PATH"] = _test_db_path

# Now we can safely import database and app
import database

database.DATABASE_PATH = _test_db_path


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initialize database once for all tests."""
    database.init_database()
    yield
    # Cleanup after all tests
    try:
        os.unlink(_test_db_path)
    except:
        pass


@pytest.fixture
def app():
    """Create Flask test app."""
    from app import app as flask_app

    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def clean_db():
    """Clean database before each test."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM nodes")
    cursor.execute("DELETE FROM sync_log")
    conn.commit()
    conn.close()
    yield
    # Cleanup after test
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM nodes")
    cursor.execute("DELETE FROM sync_log")
    conn.commit()
    conn.close()


@pytest.fixture
def test_user(clean_db):
    """Create a test user."""
    from models.user import User

    user = User.create_user(username="testuser", password="TestPass123!", role="admin")
    return user


@pytest.fixture
def test_client_with_auth(client, test_user):
    """Client with authenticated session."""
    with client.session_transaction() as sess:
        sess["username"] = test_user.username
    return client
