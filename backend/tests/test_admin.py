import os
import sys
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_PATH"] = "test_kanban.db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import db
from backend.models import User, Organization, OrganizationMember, Team, TeamMember, Board, Column
from backend.auth import create_access_token


@pytest.fixture(autouse=True)
def setup_database():
    """Reset database before each test"""
    db.drop_tables([Board, Column, TeamMember, Team, OrganizationMember, Organization, User])
    db.create_tables([User, Organization, OrganizationMember, Team, TeamMember, Board, Column])


@pytest.fixture
def admin_user():
    """Create an admin user"""
    user = User.create_user(username="admin", password="admin123", admin=True)
    return user


@pytest.fixture
def regular_user():
    """Create a regular user"""
    user = User.create_user(username="user", password="user123", admin=False)
    return user


@pytest.fixture
def admin_token(admin_user):
    """Create admin token"""
    return create_access_token(data={"sub": admin_user.id, "username": admin_user.username})


@pytest.fixture
def regular_token(regular_user):
    """Create regular user token"""
    return create_access_token(data={"sub": regular_user.id, "username": regular_user.username})


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_admin_status_admin(client, admin_token):
    """Admin user can check admin status"""
    response = client.get("/api/admin/status", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["is_admin"] is True


def test_admin_status_regular_user(client, regular_token):
    """Regular user can check admin status"""
    response = client.get("/api/admin/status", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 200
    assert response.json()["is_admin"] is False


def test_list_users_requires_admin(client, regular_token):
    """Regular users cannot list all users"""
    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {regular_token}"})
    assert response.status_code == 403


def test_list_users_admin(client, admin_token, admin_user, regular_user):
    """Admin can list all users"""
    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    usernames = [u["username"] for u in users]
    assert "admin" in usernames
    assert "user" in usernames


def test_create_user_requires_admin(client, regular_token):
    """Regular users cannot create users"""
    response = client.post(
        "/api/admin/users",
        json={"username": "newuser", "password": "password123"},
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


def test_create_user_admin(client, admin_token):
    """Admin can create a new user"""
    response = client.post(
        "/api/admin/users",
        json={"username": "newuser", "password": "password123", "email": "new@test.com"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@test.com"
    assert response.json()["admin"] is False

    # Verify user exists in database
    user = User.get_or_none(User.username == "newuser")
    assert user is not None


def test_create_admin_user(client, admin_token):
    """Admin can create another admin user"""
    response = client.post(
        "/api/admin/users",
        json={"username": "admin2", "password": "password123", "admin": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["admin"] is True


def test_update_user_requires_admin(client, regular_token, admin_user):
    """Regular users cannot update users"""
    response = client.put(
        f"/api/admin/users/{admin_user.id}",
        json={"username": "hacked"},
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


def test_update_user_admin(client, admin_token, regular_user):
    """Admin can update users"""
    response = client.put(
        f"/api/admin/users/{regular_user.id}",
        json={"username": "updated", "email": "updated@test.com", "admin": True},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updated"
    assert response.json()["email"] == "updated@test.com"
    assert response.json()["admin"] is True


def test_update_user_cannot_remove_own_admin(client, admin_token, admin_user):
    """Admin cannot remove their own admin access"""
    response = client.put(
        f"/api/admin/users/{admin_user.id}",
        json={"username": admin_user.username, "admin": False},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


def test_delete_user_requires_admin(client, regular_token, admin_user):
    """Regular users cannot delete users"""
    response = client.delete(
        f"/api/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


def test_delete_user_admin(client, admin_token, regular_user):
    """Admin can delete users"""
    user_id = regular_user.id
    response = client.delete(
        f"/api/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    # Verify user is deleted
    assert User.get_or_none(User.id == user_id) is None


def test_delete_user_cannot_delete_self(client, admin_token, admin_user):
    """Admin cannot delete themselves"""
    response = client.delete(
        f"/api/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


def test_reset_password_requires_admin(client, regular_token, admin_user):
    """Regular users cannot reset passwords"""
    response = client.post(
        f"/api/admin/users/{admin_user.id}/reset-password",
        json={"password": "newpassword"},
        headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


def test_reset_password_admin(client, admin_token, regular_user):
    """Admin can reset user passwords"""
    response = client.post(
        f"/api/admin/users/{regular_user.id}/reset-password",
        json={"password": "newpassword123"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200

    # Re-fetch user from database to verify password was changed
    user = User.get_by_id(regular_user.id)
    assert user.verify_password("newpassword123")


def test_reset_password_too_long(client, admin_token, regular_user):
    """Password reset fails if password is too long"""
    response = client.post(
        f"/api/admin/users/{regular_user.id}/reset-password",
        json={"password": "x" * 100},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
