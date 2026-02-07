import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import db
from backend.models import (
    User,
    Board,
    Column,
    Card,
    Organization,
    OrganizationMember,
    Team,
    TeamMember,
)


@pytest.fixture
def auth_headers(test_user):
    from backend.auth import create_access_token

    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username}
    )
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
        json={"username": test_user.username, "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client, test_user):
    response = client.post(
        "/api/token",
        json={"username": test_user.username, "password": "wrongpassword"},
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
    assert response.status_code == 401


def test_get_board_with_columns(client, auth_headers, test_user):
    """Get a board with its columns"""
    # Create a board
    response = client.post(
        "/api/boards",
        json={"name": "Board with Columns"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    board_id = response.json()["id"]

    # Get board - columns need to be created separately since API doesn't create defaults
    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Board with Columns"
    assert "columns" in data
    # Note: API no longer creates default columns


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

    # Create a column first since API doesn't create default columns
    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "To Do", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 200
    column_id = response.json()["id"]

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

    # Create columns first since API doesn't create default columns
    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "Column 1", "position": 0},
        headers=auth_headers,
    )
    column1_id = response.json()["id"]

    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "Column 2", "position": 1},
        headers=auth_headers,
    )
    column2_id = response.json()["id"]

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

    # Create a column first since API doesn't create default columns
    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "To Delete", "position": 0},
        headers=auth_headers,
    )
    column_id = response.json()["id"]

    response = client.post(
        "/api/cards",
        json={"column_id": column_id, "title": "Card to Delete", "position": 0},
        headers=auth_headers,
    )
    card_id = response.json()["id"]

    response = client.delete(f"/api/cards/{card_id}", headers=auth_headers)
    assert response.status_code == 200


def test_update_nonexistent_card_returns_404(client, auth_headers, test_user):
    """Test that updating a non-existent card returns 404, not 422."""
    response = client.put(
        "/api/cards/99999",
        json={"column_id": 1, "title": "Test", "description": "", "position": 0},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_nonexistent_card_returns_404(client, auth_headers, test_user):
    """Test that deleting a non-existent card returns 404."""
    response = client.delete("/api/cards/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


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


def test_reorder_cards(client, auth_headers, test_user):
    """Test reordering cards within a column"""
    # Create board and column
    response = client.post(
        "/api/boards",
        json={"name": "Reorder Cards Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    response = client.post(
        "/api/columns",
        json={"board_id": board_id, "name": "To Do", "position": 0},
        headers=auth_headers,
    )
    column_id = response.json()["id"]

    # Create multiple cards
    card_ids = []
    for i in range(3):
        response = client.post(
            "/api/cards",
            json={"column_id": column_id, "title": f"Card {i}", "position": i},
            headers=auth_headers,
        )
        card_ids.append(response.json()["id"])

    # Reorder cards: reverse their order
    reorder_request = [
        {"id": card_ids[0], "position": 2},
        {"id": card_ids[1], "position": 1},
        {"id": card_ids[2], "position": 0},
    ]

    response = client.post(
        "/api/cards/reorder",
        json={"cards": reorder_request},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify the reorder persisted by fetching the board
    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200
    cards = response.json()["columns"][0]["cards"]
    card_titles = [c["title"] for c in cards]
    assert card_titles == ["Card 2", "Card 1", "Card 0"]


def test_reorder_columns(client, auth_headers, test_user):
    """Test reordering columns on a board"""
    # Create board
    response = client.post(
        "/api/boards",
        json={"name": "Reorder Columns Board"},
        headers=auth_headers,
    )
    board_id = response.json()["id"]

    # Create multiple columns
    column_ids = []
    for i in range(3):
        response = client.post(
            "/api/columns",
            json={"board_id": board_id, "name": f"Column {i}", "position": i},
            headers=auth_headers,
        )
        column_ids.append(response.json()["id"])

    # Reorder columns: reverse their order
    reorder_request = [
        {"id": column_ids[0], "position": 2},
        {"id": column_ids[1], "position": 1},
        {"id": column_ids[2], "position": 0},
    ]

    response = client.post(
        "/api/columns/reorder",
        json={"columns": reorder_request},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify the reorder persisted by fetching the board
    response = client.get(f"/api/boards/{board_id}", headers=auth_headers)
    assert response.status_code == 200
    column_names = [c["name"] for c in response.json()["columns"]]
    assert column_names == ["Column 2", "Column 1", "Column 0"]


def test_reorder_cards_requires_auth(client):
    """Test that reordering cards requires authentication"""
    response = client.post(
        "/api/cards/reorder",
        json={"cards": [{"id": 1, "position": 0}]},
    )
    assert response.status_code == 401


def test_reorder_columns_requires_auth(client):
    """Test that reordering columns requires authentication"""
    response = client.post(
        "/api/columns/reorder",
        json={"columns": [{"id": 1, "position": 0}]},
    )
    assert response.status_code == 401
