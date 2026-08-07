"""Peewee migrations -- 001_unix_permissions.

Update the schema for Unix-like permissions:

1. Add owner_id to Organization, populated from the old
   organization_member.role == 'owner' rows
2. Add is_public_to_org to Board (default False)
3. Leave the now-orphaned role columns alone; the app ignores them

Originally a standalone script run by hand. Converted to run under
peewee-migrate so deploys apply it automatically -- see manage.py migrate.

Written to be safely re-runnable. Production applied this by hand long before
there was a migration history table, so the first router run will try it
again; every step below checks before it acts. A fresh install is also a
no-op, because init_db() creates these tables from the models with the
columns already present.
"""

import peewee as pw
from peewee_migrate import Migrator


def _table_exists(database, table):
    rows = database.execute_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchall()
    return bool(rows)


def _columns(database, table):
    return [row[1] for row in database.execute_sql(f"PRAGMA table_info({table})")]


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    if fake:
        return

    for table in ("organization", "board"):
        if not _table_exists(database, table):
            print(f"  {table} table does not exist yet, nothing to migrate")
            return

    # Capture ownership from the old role column before adding owner_id. On a
    # database that already migrated, the role column is gone and this yields
    # nothing -- which is correct, owner_id is already populated.
    org_owners = []
    try:
        org_owners = database.execute_sql("""
            SELECT om.organization_id, om.user_id, u.username, o.name
            FROM organization_member om
            JOIN user u ON om.user_id = u.id
            JOIN organization o ON om.organization_id = o.id
            WHERE om.role = 'owner'
        """).fetchall()
        print(f"  Found {len(org_owners)} organization owners to migrate")
    except pw.OperationalError:
        print("  No legacy role column to read ownership from, skipping")

    if "owner_id" in _columns(database, "organization"):
        print("  organization.owner_id already exists")
    else:
        database.execute_sql("ALTER TABLE organization ADD COLUMN owner_id INTEGER")
        print("  Added organization.owner_id")

    if "is_public_to_org" in _columns(database, "board"):
        print("  board.is_public_to_org already exists")
    else:
        database.execute_sql(
            "ALTER TABLE board ADD COLUMN is_public_to_org INTEGER DEFAULT 0"
        )
        print("  Added board.is_public_to_org")

    for org_id, user_id, username, org_name in org_owners:
        database.execute_sql(
            "UPDATE organization SET owner_id = ? WHERE id = ?", (user_id, org_id)
        )
        print(f"  Set owner_id={user_id} ({username}) on org {org_id} ({org_name})")

    # Any org still without an owner falls back to its lowest-id member.
    try:
        database.execute_sql("""
            UPDATE organization
            SET owner_id = (
                SELECT MIN(user_id) FROM organization_member
                WHERE organization_member.organization_id = organization.id
            )
            WHERE owner_id IS NULL
            AND id IN (SELECT DISTINCT organization_id FROM organization_member)
        """)
        print("  Applied fallback owners where needed")
    except pw.OperationalError:
        print("  organization_member table not found, skipping fallback owners")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """No rollback.

    SQLite cannot drop a column without rebuilding the table, and the data
    this migration recovered (ownership) has no home to go back to -- the
    role column it came from is gone.
    """
    raise NotImplementedError("001_unix_permissions cannot be rolled back")
