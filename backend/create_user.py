#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import db
from backend.models import User


def create_user(username, password, email=None, admin=False):
    try:
        user = User.create_user(username, password, email=email, admin=admin)
        print(f"User '{username}' created successfully with id={user.id}")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password> [--email EMAIL] [--admin]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    email = None
    admin = False

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--email" and i + 1 < len(sys.argv):
            email = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--admin":
            admin = True
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)

    db.connect()
    success = create_user(username, password, email=email, admin=admin)
    db.close()

    sys.exit(0 if success else 1)
