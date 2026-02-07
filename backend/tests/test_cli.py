import os
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

tmp_dir = tempfile.mkdtemp()


# Use a temporary config directory for tests
@pytest.fixture(autouse=True)
def temp_config_dir():
    original_env = os.environ.get("KANBAN_CONFIG_DIR")
    os.environ["KANBAN_CONFIG_DIR"] = tmp_dir
    yield tmp_dir
    if original_env is not None:
        os.environ["KANBAN_CONFIG_DIR"] = original_env
    else:
        del os.environ["KANBAN_CONFIG_DIR"]


import sys

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
from backend.auth import create_access_token


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    return TestClient(app)


def test_config_url():
    from kanban.config import get_server_url, set_server_url, load_config

    set_server_url("http://test.example.com")
    assert get_server_url() == "http://test.example.com"
    config = load_config()
    assert config["server"]["url"] == "http://test.example.com"


def test_token_storage():
    from kanban.config import get_token, set_token, clear_token

    set_token("test-token-123")
    assert get_token() == "test-token-123"
    clear_token()
    assert get_token() is None


def test_cli_login_command(client, test_cli_user):
    from kanban.cli import cmd_login
    from kanban.config import get_token
    from kanban.client import KanbanClient

    with patch.object(KanbanClient, "__init__", return_value=None) as mock_init:
        with patch.object(
            KanbanClient, "login", return_value="fake-jwt-token"
        ) as mock_login:
            cmd_login(
                username="testuser",
                password="testpassword",
                server="http://localhost:8000",
            )
            token = get_token()
            assert token == "fake-jwt-token"


def test_cli_logout_command():
    from kanban.cli import cmd_logout
    from kanban.config import set_token, get_token

    set_token("some-token")
    assert get_token() == "some-token"

    cmd_logout()
    assert get_token() is None


def test_cli_boards_command(client, auth_headers, test_user):
    from kanban.cli import cmd_boards
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.boards.return_value = [
        {"id": 1, "name": "Test Board"},
        {"id": 2, "name": "Another Board"},
    ]

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_boards()

        mock_client.boards.assert_called_once()


def test_cli_board_create_command(client, auth_headers, test_user):
    from kanban.cli import cmd_board_create
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.board_create.return_value = {"id": 42}

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_board_create(name="New Board")

        mock_client.board_create.assert_called_once_with("New Board")


def test_cli_card_create_command(client, auth_headers, test_user):
    from kanban.cli import cmd_card_create
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.card_create.return_value = {"id": 99}

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_card_create(
            column_id=5, title="Test Card", description="A test description", position=0
        )

        mock_client.card_create.assert_called_once_with(
            5, "Test Card", "A test description", 0
        )


def test_cli_card_update_command(client, auth_headers, test_user):
    from kanban.cli import cmd_card_update
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.card_update.return_value = {"id": 99}

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_card_update(
            card_id=99,
            title="Updated Card",
            description="Updated description",
            position=1,
            column=3,
        )

        mock_client.card_update.assert_called_once_with(
            99, "Updated Card", "Updated description", 1, 3
        )


def test_cli_board_delete_command(client, auth_headers, test_user):
    from kanban.cli import cmd_board_delete
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.board_delete.return_value = True

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_board_delete(board_id=42)

        mock_client.board_delete.assert_called_once_with(42)


def test_cli_card_delete_command(client, auth_headers, test_user):
    from kanban.cli import cmd_card_delete
    from kanban.config import set_token
    from kanban.client import KanbanClient

    set_token("test-token")

    mock_client = MagicMock()
    mock_client.card_delete.return_value = True

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_card_delete(card_id=99)

        mock_client.card_delete.assert_called_once_with(99)
