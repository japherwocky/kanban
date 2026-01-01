#!/usr/bin/env python
"""
Database management script for the Kanban server.

Usage (from project root):
    python -m backend.manage init     - Create all tables
    python -m backend.manage wipe     - Drop and recreate all tables (destructive)
    python -m backend.manage reset    - Alias for wipe
    python -m backend.manage status   - Show database status
"""
import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import db
from backend.models import User, Board, Column, Card, Organization, OrganizationMember, Team, TeamMember


TABLES = [User, Board, Column, Card, Organization, OrganizationMember, Team, TeamMember]


def cmd_init():
    """Create all database tables."""
    db.connect()
    db.create_tables(TABLES)
    db.close()
    print("Database initialized. Tables created:")
    for model in TABLES:
        print(f"  - {model.__name__}")


def cmd_wipe():
    """Drop all tables and recreate them. DESTROYS ALL DATA."""
    print("WARNING: This will delete ALL data in the database.")
    confirm = input("Type 'yes' to continue: ")
    if confirm != "yes":
        print("Aborted.")
        sys.exit(1)

    db.connect()
    db.drop_tables(TABLES)
    print("Tables dropped.")
    db.create_tables(TABLES)
    db.close()
    print("Database wiped and recreated. Tables created:")
    for model in TABLES:
        print(f"  - {model.__name__}")


def cmd_status():
    """Show database status."""
    db.connect()
    print("Database status:")
    print(f"  Path: {db.database}")
    print("  Tables:")
    for model in TABLES:
        count = model.select().count()
        print(f"    - {model.__name__}: {count} records")
    db.close()


def main():
    parser = argparse.ArgumentParser(
        prog="python -m backend.manage",
        description="Kanban server database management"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    sp_init = subparsers.add_parser("init", help="Create all database tables")
    sp_init.set_defaults(func=cmd_init)

    sp_wipe = subparsers.add_parser("wipe", help="Drop and recreate all tables (destructive)")
    sp_wipe.set_defaults(func=cmd_wipe)

    sp_reset = subparsers.add_parser("reset", help="Alias for wipe")
    sp_reset.set_defaults(func=cmd_wipe)

    sp_status = subparsers.add_parser("status", help="Show database status")
    sp_status.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        print("\nExamples:")
        print("  python -m backend.manage init      # Create tables")
        print("  python -m backend.manage wipe      # Delete all data and recreate")
        print("  python -m backend.manage status    # Show record counts")
        sys.exit(1)

    args.func()


if __name__ == "__main__":
    main()
