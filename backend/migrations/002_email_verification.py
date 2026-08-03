"""Peewee migrations -- 002_email_verification.

Support self-serve signup with email verification:

1. Add email_verified to User
2. Mark every pre-existing user as verified
3. Add a unique index on User.email

Step 2 is the subtle one. The column defaults to 0 and login refuses
unverified users, so without the backfill every account that predates this
migration -- including any admin -- would be locked out. It is deliberately
tied to having just created the column: on a re-run it must not re-verify
accounts that have since signed up and genuinely not confirmed yet.

The emailverificationtoken table is not created here. init_db() calls
create_tables(), which adds missing tables on the next start.
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

    if not _table_exists(database, "user"):
        print("  user table does not exist yet, nothing to migrate")
        return

    if "email_verified" in _columns(database, "user"):
        # Either a fresh install, where create_tables() already built the
        # column from the model, or a re-run. Either way the backfill below
        # must not fire: a fresh database has no legacy accounts, and a re-run
        # would wrongly verify real pending signups.
        print("  user.email_verified already exists, skipping backfill")
    else:
        database.execute_sql(
            "ALTER TABLE user ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0"
        )
        print("  Added user.email_verified")

        cursor = database.execute_sql("UPDATE user SET email_verified = 1")
        print(f"  Marked {cursor.rowcount} pre-existing users verified")

    # Nothing stopped two accounts sharing an address until now. Which one
    # keeps it is a human decision, so refuse rather than guess.
    duplicates = database.execute_sql("""
        SELECT email, COUNT(*) FROM user
        WHERE email IS NOT NULL AND email != ''
        GROUP BY email HAVING COUNT(*) > 1
    """).fetchall()

    if duplicates:
        lines = []
        for email, count in duplicates:
            holders = database.execute_sql(
                "SELECT id, username FROM user WHERE email = ?", (email,)
            ).fetchall()
            who = ", ".join(f"{name} (id={uid})" for uid, name in holders)
            lines.append(f"    {email}: {count} accounts -> {who}")
        raise RuntimeError(
            "Cannot add a unique index on user.email -- duplicates exist:\n"
            + "\n".join(lines)
            + "\n  Clear or change the email on all but one account of each "
            "set, then deploy again."
        )

    # Named user_email, not something of our own choosing, because that is
    # what peewee generates for `email = CharField(unique=True)` when
    # create_tables() builds a fresh database. Matching it means a migrated
    # database and a fresh install converge on exactly one index with one
    # name, instead of the fresh install carrying both and drifting.
    #
    # NULLs are exempt from a unique index in SQLite, so accounts with no
    # email at all are unaffected.
    database.execute_sql(
        "CREATE UNIQUE INDEX IF NOT EXISTS user_email ON user(email)"
    )
    print("  Unique index user_email in place")


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Drop the unique index.

    The column itself stays: SQLite cannot drop one without rebuilding the
    table, and leaving it costs nothing because older code never selects it.
    """
    database.execute_sql("DROP INDEX IF EXISTS user_email")
