import os
import pytest
import random
import string
from backend.database import db
from backend.models import (
    User,
    Board,
    Column,
    Card,
    Comment,
    Organization,
    OrganizationMember,
    Team,
    TeamMember,
    ApiKey,
)


@pytest.fixture(scope="session")
def setup_test_db():
    """Session-scoped fixture to manage database state across tests"""
    original_db_path = os.environ.get("DATABASE_PATH")

    # Override database path for tests
    os.environ["DATABASE_PATH"] = "test_kanban.db"

    yield

    # Restore original database path
    if original_db_path:
        os.environ["DATABASE_PATH"] = original_db_path
    else:
        os.environ.pop("DATABASE_PATH", None)

    # Clean up any test database files
    for db_file in ["test_kanban.db", "test_kanban_cli.db"]:
        if os.path.exists(db_file):
            os.remove(db_file)


@pytest.fixture
def test_db(setup_test_db):
    """Per-test database fixture"""
    # Clean up any existing test database
    if os.path.exists("test_kanban.db"):
        os.remove("test_kanban.db")

    # Close any existing connections
    try:
        db.close()
    except:
        pass

    db.connect()
    db.create_tables(
        [
            User,
            Board,
            Column,
            Card,
            Comment,
            Organization,
            OrganizationMember,
            Team,
            TeamMember,
            ApiKey,
        ]
    )

    yield db

    # Close connection cleanly
    try:
        db.close()
    except:
        pass

    # Clean up test database
    if os.path.exists("test_kanban.db"):
        os.remove("test_kanban.db")


@pytest.fixture
def test_user(test_db):
    """Create a unique test user"""
    random_suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{random_suffix}"
    user = User.create_user(username, "testpassword")
    return user


@pytest.fixture
def test_cli_db(setup_test_db):
    """CLI test database fixture"""
    # Override for CLI tests
    os.environ["DATABASE_PATH"] = "test_kanban_cli.db"

    # Clean up any existing test database
    if os.path.exists("test_kanban_cli.db"):
        os.remove("test_kanban_cli.db")

    # Close any existing connections
    try:
        db.close()
    except:
        pass

    db.connect()
    db.create_tables(
        [
            User,
            Board,
            Column,
            Card,
            Comment,
            Organization,
            OrganizationMember,
            Team,
            TeamMember,
            ApiKey,
        ]
    )

    yield db

    # Close connection cleanly
    try:
        db.close()
    except:
        pass

    # Clean up test database
    if os.path.exists("test_kanban_cli.db"):
        os.remove("test_kanban_cli.db")

    # Restore to regular test database
    os.environ["DATABASE_PATH"] = "test_kanban.db"


@pytest.fixture
def test_cli_user(test_cli_db):
    """Create a unique CLI test user"""
    random_suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{random_suffix}"
    user = User.create_user(username, "testpassword")
    return user
