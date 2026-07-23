import os

# MUST run before anything imports backend.database, which builds its
# SqliteDatabase from DATABASE_PATH at import time.
#
# Rebinding the db afterwards does not work: backend/models.py captures the
# database OBJECT in BaseModel.Meta.database, and backend/api.py captures the
# same object via `from backend.database import db` for its db.atomic() calls.
# Reassigning backend.database.db only moves the module attribute, leaving
# both pointing at the real kanban.db -- which is how the suite used to wipe
# the developer's local database on every run. Pointing DATABASE_PATH at a
# test database before import means only one db object is ever created, so
# models, transactions, and fixtures all agree on it.
#
# A shared-cache URI rather than plain ":memory:" because the FastAPI
# TestClient serves requests on a different thread, and peewee opens a
# connection per thread. Plain ":memory:" would give each thread its own
# empty database; cache=shared makes them the same one for the process.
os.environ["DATABASE_PATH"] = "file:kanban_test?mode=memory&cache=shared"

import pytest  # noqa: E402
import random  # noqa: E402
import string  # noqa: E402

from backend.database import db as _db  # noqa: E402

TEST_MODELS = None


def _models():
    global TEST_MODELS
    if TEST_MODELS is None:
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
            OrganizationInvite,
        )

        TEST_MODELS = [
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
            OrganizationInvite,
        ]
    return TEST_MODELS


@pytest.fixture(scope="session")
def _setup_test_db():
    """Session-scoped fixture to create tables once."""
    assert _db.database.startswith("file:kanban_test"), (
        f"tests are pointed at {_db.database!r}, not the test database. "
        "Something imported backend.database before conftest set DATABASE_PATH."
    )

    # Held open for the whole session: the shared-cache in-memory database is
    # discarded once the last connection to it closes.
    _db.connect()
    _db.create_tables(_models())
    yield
    _db.close()


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
        OrganizationInvite,
    )

    # Clear all table data using peewee's delete method
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
        OrganizationInvite,
        User,
    ]:
        try:
            table.delete().execute()
        except:
            pass
    yield _db


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


@pytest.fixture
def test_cli_user(db_session):
    """Create a unique CLI test user."""
    from backend.models import User

    random_suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{random_suffix}"
    user = User.create_user(username, "testpassword")
    return user
