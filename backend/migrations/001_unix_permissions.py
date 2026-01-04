"""
Migration to update database schema for Unix-like permissions.

Changes:
1. Add owner_id column to Organization table
2. Add is_public_to_org column to Board table (default False)
3. Role columns in OrganizationMember and TeamMember will be ignored

This migration is for SQLite which has limited ALTER TABLE support.

Run from the project root: python backend/migrations/001_unix_permissions.py
"""

import sqlite3
import os


def migrate():
    db_path = os.path.join(os.getcwd(), "kanban.db")

    if not os.path.exists(db_path):
        print("No database file found at:", db_path)
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Starting migration...")

    # Step 1: Check current schema
    print("Step 1: Checking current schema...")
    cursor.execute("PRAGMA table_info(organization)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"  Current organization columns: {columns}")

    cursor.execute("PRAGMA table_info(board)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"  Current board columns: {columns}")

    # Step 2: Back up existing organization owners (from organization_member.role = 'owner')
    print("\nStep 2: Backing up organization ownership data...")
    try:
        cursor.execute("""
            SELECT om.organization_id, om.user_id, u.username, o.name
            FROM organization_member om
            JOIN user u ON om.user_id = u.id
            JOIN organization o ON om.organization_id = o.id
            WHERE om.role = 'owner'
        """)
        org_owners = cursor.fetchall()
        print(f"  Found {len(org_owners)} organization owners to migrate")
        for org_id, user_id, username, org_name in org_owners:
            print(f"    Org '{org_name}' (id={org_id}) -> owner: {username} (id={user_id})")
    except sqlite3.OperationalError as e:
        print(f"  Warning: Could not query organization members: {e}")
        org_owners = []

    # Step 3: Add owner_id column to organization table
    print("\nStep 3: Adding owner_id column to organization table...")
    try:
        cursor.execute("ALTER TABLE organization ADD COLUMN owner_id INTEGER")
        print("  Added owner_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  Column already exists, skipping...")
        else:
            print(f"  Error: {e}")

    # Step 4: Add is_public_to_org column to board table
    print("\nStep 4: Adding is_public_to_org column to board table...")
    try:
        cursor.execute("ALTER TABLE board ADD COLUMN is_public_to_org INTEGER DEFAULT 0")
        print("  Added is_public_to_org column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  Column already exists, skipping...")
        else:
            print(f"  Error: {e}")

    # Step 5: Update organization owner_id values
    print("\nStep 5: Setting organization owners...")
    for org_id, user_id, username, org_name in org_owners:
        cursor.execute("UPDATE organization SET owner_id = ? WHERE id = ?", (user_id, org_id))
        print(f"  Set owner_id={user_id} for org id={org_id} ({org_name})")

    # Step 6: Handle organizations that might not have an owner set
    print("\nStep 6: Setting fallback owners for any orgs without owner...")
    try:
        cursor.execute("""
            UPDATE organization
            SET owner_id = (
                SELECT MIN(user_id) FROM organization_member
                WHERE organization_member.organization_id = organization.id
            )
            WHERE owner_id IS NULL
            AND id IN (SELECT DISTINCT organization_id FROM organization_member)
        """)
        print(f"  Updated {cursor.rowcount} organizations with fallback owners")
    except sqlite3.OperationalError:
        print("  (organization_member table not found, skipping fallback owners)")

    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("Migration completed successfully!")
    print("="*60)
    print("\nNote: role columns in organization_member and team_member tables")
    print("      are now orphaned and will be ignored by the application.")
    print("\nThe new permission model:")
    print("  - Organization has an explicit owner (like root)")
    print("  - Board can be shared with one team or made public to org")
    print("  - Any team member can add other org members to the team")


if __name__ == "__main__":
    migrate()
