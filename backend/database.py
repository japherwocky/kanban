import os
from peewee import SqliteDatabase

DATABASE_PATH = os.environ.get("DATABASE_PATH", "kanban.db")

# A "file:..." DATABASE_PATH is an SQLite URI and needs uri=True to be parsed
# as one rather than treated as a literal filename. The test suite uses this
# to get a shared in-memory database.
db = SqliteDatabase(DATABASE_PATH, uri=DATABASE_PATH.startswith("file:"))


def init_db():
    # Skip if already connected (e.g., in tests)
    if db.is_connection_usable():
        return

    db.connect()
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
        BetaSignup,
        ApiKey,
        OrganizationInvite,
    )

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
            BetaSignup,
            ApiKey,
            OrganizationInvite,
        ]
    )
    db.close()
