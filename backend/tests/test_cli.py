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
    original_env = os.environ.get("KANBAN_CONFIG_PATH")
    tmp_config = os.path.join(tmp_dir, ".kanban.yaml")
    os.environ["KANBAN_CONFIG_PATH"] = tmp_config
    yield tmp_config
    if original_env is not None:
        os.environ["KANBAN_CONFIG_PATH"] = original_env
    else:
        del os.environ["KANBAN_CONFIG_PATH"]


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


def test_cli_login_uses_configured_url_when_server_omitted(client, test_cli_user):
    """`kanban config --url ...` then `kanban login` must hit the configured
    server, not a hardcoded localhost."""
    from kanban.cli import cmd_login
    from kanban.config import set_server_url, get_server_url
    from kanban.client import KanbanClient

    set_server_url("https://kanban.example.com")

    with patch.object(KanbanClient, "__init__", return_value=None) as mock_init:
        with patch.object(KanbanClient, "login", return_value="jwt"):
            cmd_login(username="testuser", password="pw", server=None)

    # The client was pointed at the configured URL...
    assert mock_init.call_args.kwargs["server_url"] == "https://kanban.example.com"
    # ...and an omitted --server leaves the configured URL untouched.
    assert get_server_url() == "https://kanban.example.com"


def test_cli_login_persists_explicit_server(client, test_cli_user):
    """An explicit --server is saved so later commands reuse the same server."""
    from kanban.cli import cmd_login
    from kanban.config import set_server_url, get_server_url
    from kanban.client import KanbanClient

    set_server_url("http://localhost:8000")

    with patch.object(KanbanClient, "__init__", return_value=None) as mock_init:
        with patch.object(KanbanClient, "login", return_value="jwt"):
            cmd_login(
                username="testuser",
                password="pw",
                server="https://kanban.example.com",
            )

    assert mock_init.call_args.kwargs["server_url"] == "https://kanban.example.com"
    assert get_server_url() == "https://kanban.example.com"


def test_cli_login_failure_does_not_change_config(client, test_cli_user):
    """A failed login must not persist the URL or a token."""
    from kanban.cli import cmd_login
    from kanban.config import set_server_url, get_server_url, get_token, clear_token
    from kanban.client import KanbanClient
    import typer

    # The config file is shared across this module's tests, so start clean.
    set_server_url("http://localhost:8000")
    clear_token()

    with patch.object(KanbanClient, "__init__", return_value=None):
        with patch.object(KanbanClient, "login", side_effect=Exception("nope")):
            with pytest.raises(typer.Exit):
                cmd_login(
                    username="testuser",
                    password="pw",
                    server="https://kanban.example.com",
                )

    assert get_server_url() == "http://localhost:8000"
    assert get_token() is None


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


# === Network / HTTP error reporting ===


def _client_raising(exc):
    """A KanbanClient whose underlying session always raises exc."""
    from kanban.client import KanbanClient

    kanban_client = KanbanClient(server_url="http://localhost:9999", token="t")
    kanban_client.session = MagicMock()
    kanban_client.session.request.side_effect = exc
    return kanban_client


def test_client_connection_error_is_actionable():
    import requests
    from kanban.client import KanbanError

    kanban_client = _client_raising(requests.exceptions.ConnectionError())

    with pytest.raises(KanbanError) as excinfo:
        kanban_client.boards()

    message = str(excinfo.value)
    assert "Could not reach the Kanban server" in message
    assert "http://localhost:9999" in message


def test_client_timeout_is_actionable():
    import requests
    from kanban.client import KanbanError

    kanban_client = _client_raising(requests.exceptions.Timeout())

    with pytest.raises(KanbanError) as excinfo:
        kanban_client.boards()

    assert "took too long to respond" in str(excinfo.value)


def test_client_url_without_scheme_is_actionable():
    import requests
    from kanban.client import KanbanError

    kanban_client = _client_raising(requests.exceptions.InvalidSchema())

    with pytest.raises(KanbanError) as excinfo:
        kanban_client.boards()

    assert "http:// or https://" in str(excinfo.value)


def test_client_sets_a_request_timeout():
    """Without a timeout a hung server makes the CLI wait forever."""
    from kanban.client import KanbanClient, DEFAULT_TIMEOUT

    kanban_client = KanbanClient(server_url="http://localhost:9999", token="t")
    kanban_client.session = MagicMock()
    kanban_client.session.request.return_value.json.return_value = []

    kanban_client.boards()

    assert kanban_client.session.request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT


def test_client_http_error_still_propagates():
    """Commands catch HTTPError themselves; the client must not swallow it."""
    import requests

    kanban_client = _client_raising(requests.exceptions.HTTPError())

    with pytest.raises(requests.exceptions.HTTPError):
        kanban_client.boards()


@pytest.mark.parametrize(
    "status,expected",
    [
        (401, "Not authenticated"),
        (403, "permission"),
        (404, "Not found"),
        (500, "server returned an error"),
    ],
)
def test_describe_http_error(status, expected):
    import requests
    from kanban.cli import describe_http_error

    response = MagicMock()
    response.status_code = status
    response.json.side_effect = ValueError
    response.text = "boom"

    message = describe_http_error(requests.exceptions.HTTPError(response=response))
    assert expected.lower() in message.lower()


def test_describe_http_error_prefers_server_detail():
    import requests
    from kanban.cli import describe_http_error

    response = MagicMock()
    response.status_code = 404
    response.json.return_value = {"detail": "Board not found"}

    message = describe_http_error(requests.exceptions.HTTPError(response=response))
    assert message == "Board not found"
