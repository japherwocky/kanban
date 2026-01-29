import os
from peewee import SqliteDatabase

DATABASE_PATH = os.environ.get("DATABASE_PATH", "kanban.db")

db = SqliteDatabase(DATABASE_PATH)


def init_db():
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
        ]
    )
    db.close()
