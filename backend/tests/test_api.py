import os
import sys
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

os.environ["DATABASE_PATH"] = "test_kanban.db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import db
from backend.models import User, Board, Column, Card, Organization, OrganizationMember, Team, TeamMember





@pytest.fixture
def test_user(test_db):
    user = User.create_user("testuser", "testpassword")
    return user


@pytest.fixture
def auth_headers(test_user):
    from backend.auth import create_access_token

    token = create_access_token(data={"sub": test_user.id, "username": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


def test_server_launch():
    from backend.main import app
    from backend.database import db
    from backend.models import User, Board, Column, Card
    assert app is not None
    assert db is not None


def test_root(client):
    response = client.get("/")
    assert response.status_code in [200, 404]


def test_login_success(client, test_user):
    response = client.post(
        "/api/token",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client, test_user):
    response = client.post(
        "/api/token",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_create_board(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Test Board"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    # Verify all required fields are present for frontend display
    assert "name" in data
    assert data["name"] == "Test Board"
    assert "created_at" in data
    assert data["created_at"] is not None
    assert "shared_team_id" in data
    assert data["shared_team_id"] is None
    assert "owner_id" in data
    assert data["owner_id"] == test_user.id


def test_list_boards(client, auth_headers, test_user):
    response = client.get("/api/boards", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_board_without_auth(client):
    response = client.post(
        "/api/boards",
        json={"name": "Test Board"},
    )
    assert response.status_code == 403


def test_get_board_with_columns(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Board with Columns"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    board_id = response.json()["id"]

    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Board with Columns"
    assert "columns" in data
    assert len(data["columns"]) == 3
    assert data["owner_id"] == test_user.id
    assert data["shared_team_id"] is None


def test_create_column(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Column Test Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "New Column", "position": 3},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Column"


def test_create_card(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Card Test Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    column_id = response.json()["columns"][0]["id"]

    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Test Card", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Card"


def test_move_card(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Move Card Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    columns = response.json()["columns"]
    column1_id = columns[0]["id"]
    column2_id = columns[1]["id"]

    response = client.post(
        "/api/cards",
        json={"column_id": column1_id, "title": "Card to Move", "position": 0},
        headers=auth_headers,
    )
    card_id = response.json()["id"]

    response = client.put(
        f"/api/cards/{card_id}",
        json={"column_id": column2_id, "title": "Card to Move", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_delete_card(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Delete Card Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    column_id = response.json()["columns"][0]["id"]

    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Card to Delete", "position": 0},
        headers=auth_headers,
    )
    card_id = response.json()["id"]

    response = client.delete(f"/api/cards/{card_id}", headers=auth_headers)
    assert response.status_code == 200


def test_delete_board(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Board to Delete"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.delete(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 404
