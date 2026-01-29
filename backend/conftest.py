import pytest
import random
import string
from peewee import SqliteDatabase

# Create an in-memory database for tests
_test_db = SqliteDatabase(":memory:")


@pytest.fixture(scope="session")
def _setup_test_db():
    """Session-scoped fixture to create tables once."""
    import backend.database as db_module
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
        BetaSignup,
    )

    # Replace the module-level db with our test database
    db_module.db = _test_db

    # Connect and create tables
    _test_db.connect()
    _test_db.create_tables(
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
            BetaSignup,
        ]
    )
    yield
    _test_db.close()


@pytest.fixture
def db_session(_setup_test_db):
    """Per-test database fixture that clears all data between tests."""
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
        BetaSignup,
    )

    # Clear all table data (in reverse dependency order to avoid FK issues)
    for table in [
        Card,
        Comment,
        Column,
        Board,
        TeamMember,
        Team,
        OrganizationMember,
        Organization,
        ApiKey,
        BetaSignup,
        User,
    ]:
        try:
            _test_db.execute_sql(f"DELETE FROM {table._meta.table_name}")
        except:
            pass
    yield _test_db


@pytest.fixture
def test_user(db_session):
    """Create a unique test user"""
    from backend.models import User

    random_suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{random_suffix}"
    user = User.create_user(username, "testpassword")
    return user


# Alias for backwards compatibility with tests expecting test_db
@pytest.fixture
def test_db(db_session):
    """Alias for db_session for backwards compatibility."""
    return db_session
