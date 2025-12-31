#!/usr/bin/env python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import db
from backend.models import User


def create_user(username, password):
    try:
        user = User.create_user(username, password)
        print(f"User '{username}' created successfully with id={user.id}")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    db.connect()
    success = create_user(username, password)
    db.close()

    sys.exit(0 if success else 1)
