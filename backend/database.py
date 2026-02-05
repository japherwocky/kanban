import os
from peewee import SqliteDatabase

DATABASE_PATH = os.environ.get("DATABASE_PATH", "kanban.db")

db = SqliteDatabase(DATABASE_PATH)


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
