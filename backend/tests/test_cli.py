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


def test_cli_api_key_flag_does_not_persist_to_config():
    """`kanban --api-key <key> <command>` must authenticate that one
    invocation without overwriting the user's saved token/API key on disk
    (regression: it used to call clear_token()+set_api_key(), silently
    logging the user out and persisting the key to ~/.kanban.yaml)."""
    import sys
    from kanban import cli
    from kanban.config import (
        set_token,
        get_token,
        get_api_key,
        set_runtime_api_key,
        get_runtime_api_key,
    )

    set_token("existing-session-token")
    set_runtime_api_key(None)

    argv = ["kanban", "--api-key", "kanban_test_key", "board", "list"]
    with patch.object(sys, "argv", argv):
        with patch("kanban.cli.app"):
            cli.main()

    try:
        assert get_runtime_api_key() == "kanban_test_key"
        assert get_token() == "existing-session-token"
        assert get_api_key() is None
    finally:
        set_runtime_api_key(None)


def test_make_client_prefers_runtime_api_key_over_stored_credentials():
    from kanban.cli import make_client
    from kanban.config import set_token, set_runtime_api_key

    set_token("stored-token")
    set_runtime_api_key("kanban_runtime_key")

    try:
        client = make_client()
        assert client.api_key == "kanban_runtime_key"
        assert client.session.headers["X-API-Key"] == "kanban_runtime_key"
        assert "Authorization" not in client.session.headers
    finally:
        set_runtime_api_key(None)


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


# === Machine-readable output (--json / KANBAN_OUTPUT=json) ===


@pytest.fixture
def json_mode():
    """Turn on JSON output for one test and put it back afterwards."""
    from kanban.output import set_json_output

    set_json_output(True)
    yield
    set_json_output(None)


@pytest.fixture(autouse=True)
def _reset_output_mode():
    from kanban.output import set_json_output

    set_json_output(None)
    yield
    set_json_output(None)


def test_json_output_emits_raw_api_response(capsys, json_mode):
    """--json prints the API payload verbatim, so a script can index into it
    instead of regexing prose out of the human rendering."""
    import json
    from kanban.cli import cmd_boards

    payload = [
        {"id": 1, "name": "Dev", "shared_team_id": 1},
        {"id": 3, "name": "Other", "shared_team_id": None},
    ]
    mock_client = MagicMock()
    mock_client.boards.return_value = payload

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_boards()

    assert json.loads(capsys.readouterr().out) == payload


def test_json_output_gives_ids_without_parsing_prose(capsys, json_mode):
    """The case from the ticket: 'Column created with id=17' needed a regex.
    The id now comes off a parsed object."""
    import json
    from kanban.cli import cmd_column_create

    mock_client = MagicMock()
    mock_client.column_create.return_value = {"id": 17, "name": "Todo", "position": 0}

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_column_create(board_id=1, name="Todo", position=0)

    assert json.loads(capsys.readouterr().out)["id"] == 17


def test_human_output_is_unchanged_by_default(capsys):
    from kanban.cli import cmd_column_create

    mock_client = MagicMock()
    mock_client.column_create.return_value = {"id": 17}

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_column_create(board_id=1, name="Todo", position=0)

    out = capsys.readouterr().out
    assert "Column created with id=17" in out
    assert "{" not in out


def test_kanban_output_env_var_selects_json(capsys, monkeypatch):
    import json
    from kanban.cli import cmd_boards

    monkeypatch.setenv("KANBAN_OUTPUT", "json")

    mock_client = MagicMock()
    mock_client.boards.return_value = [{"id": 1, "name": "Dev"}]

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_boards()

    assert json.loads(capsys.readouterr().out) == [{"id": 1, "name": "Dev"}]


def test_json_errors_go_to_stderr_leaving_stdout_parseable(capsys, json_mode):
    """A script must be able to parse stdout without first checking whether it
    holds a result or an error message."""
    import json
    import requests
    import typer
    from kanban.cli import cmd_card_delete

    response = MagicMock()
    response.status_code = 404
    mock_client = MagicMock()
    mock_client.card_delete.side_effect = requests.exceptions.HTTPError(
        response=response
    )

    with patch("kanban.cli.make_client", return_value=mock_client):
        with pytest.raises(typer.Exit):
            cmd_card_delete(card_id=42)

    captured = capsys.readouterr()
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error["status"] == 404
    assert "42" in error["error"]


def test_json_login_does_not_print_the_access_token(capsys, json_mode):
    """The token is already saved to config, and stdout is what CI logs."""
    import json
    from kanban.cli import cmd_login

    mock_client = MagicMock()
    mock_client.login.return_value = "secret-token-value"

    with patch("kanban.cli.KanbanClient", return_value=mock_client):
        cmd_login(username="alice", password="pw", server=None)

    captured = capsys.readouterr()
    assert "secret-token-value" not in captured.out
    assert json.loads(captured.out)["username"] == "alice"


@pytest.mark.parametrize(
    "argv,expected_found,expected_argv",
    [
        # Typed after the subcommand -- click would reject it, so main() strips it.
        (
            ["kanban", "board", "list", "--json"],
            True,
            ["kanban", "board", "list"],
        ),
        # Typed as a root option, which click would accept anyway.
        (["kanban", "--json", "board", "list"], True, ["kanban", "board", "list"]),
        (["kanban", "board", "list"], False, ["kanban", "board", "list"]),
        # Following an option, "--json" is that option's value, not our flag.
        (
            ["kanban", "card", "create", "1", "t", "--description", "--json"],
            False,
            ["kanban", "card", "create", "1", "t", "--description", "--json"],
        ),
    ],
)
def test_extract_json_flag_positions(argv, expected_found, expected_argv):
    from kanban.cli import _extract_json_flag

    assert _extract_json_flag(argv) is expected_found
    assert argv == expected_argv


def test_cli_card_get_shows_the_description(capsys):
    """`card` had create/update/delete but no way to read a card, so a
    description was unreachable from the CLI."""
    from kanban.cli import cmd_card_get

    mock_client = MagicMock()
    mock_client.card_get.return_value = {
        "id": 92,
        "title": "A card",
        "description": "The body you could not read.",
        "position": 0,
        "column_id": 4,
        "column_name": "Todo",
        "board_id": 1,
        "board_name": "Dev",
        "comments": [],
    }

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_card_get(card_id=92)

    out = capsys.readouterr().out
    mock_client.card_get.assert_called_once_with(92)
    assert "The body you could not read." in out
    assert "Todo" in out


def test_cli_card_get_json_emits_raw_response(capsys, json_mode):
    import json
    from kanban.cli import cmd_card_get

    payload = {
        "id": 92,
        "title": "A card",
        "description": "body",
        "position": 0,
        "column_id": 4,
        "column_name": "Todo",
        "board_id": 1,
        "board_name": "Dev",
        "comments": [],
    }
    mock_client = MagicMock()
    mock_client.card_get.return_value = payload

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_card_get(card_id=92)

    assert json.loads(capsys.readouterr().out) == payload


def test_cli_card_get_does_not_interpret_description_as_markup(capsys):
    """Descriptions are user-written text. Rendered as rich markup, a stray
    tag would silently eat characters -- or blow up on a malformed one."""
    from kanban.cli import cmd_card_get

    mock_client = MagicMock()
    mock_client.card_get.return_value = {
        "id": 1,
        "title": "t",
        "description": r"use re.search(r'id=(\d+)') on [bold] output",
        "position": 0,
        "column_id": 1,
        "column_name": "c",
        "board_id": 1,
        "board_name": "b",
        "comments": [],
    }

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_card_get(card_id=1)

    assert "[bold]" in capsys.readouterr().out


def test_cli_card_move_does_not_send_a_title():
    """The whole point of `card move`: moving used to require retyping the
    exact title, and one wrong character silently renamed the card."""
    from kanban.cli import cmd_card_move

    mock_client = MagicMock()
    mock_client.card_update.return_value = {"id": 7}

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_card_move(card_id=7, column=5, position=None)

    mock_client.card_update.assert_called_once_with(7, None, None, None, 5)


def test_cli_card_update_leaves_the_title_alone_when_omitted():
    from kanban.cli import cmd_card_update

    mock_client = MagicMock()
    mock_client.card_update.return_value = {"id": 7}

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_card_update(
            card_id=7, title=None, description=None, position=None, column=5
        )

    mock_client.card_update.assert_called_once_with(7, None, None, None, 5)


def test_client_card_update_omits_unset_fields():
    """A move must not carry a title, and the endpoint leaves out what it is
    not sent."""
    from kanban.client import KanbanClient

    client = KanbanClient(server_url="http://example.test", api_key="k")
    with patch.object(client, "_request", return_value={}) as request:
        client.card_update(7, column_id=5)

    assert request.call_args.kwargs["json"] == {"column_id": 5}


@pytest.mark.parametrize(
    "command,kwargs",
    [
        ("update", {"title": None, "description": None, "position": None, "column": None}),
        ("move", {"column": None, "position": None}),
    ],
)
def test_cli_card_change_with_nothing_to_do_errors(command, kwargs):
    import typer
    from kanban.cli import cmd_card_update, cmd_card_move

    fn = cmd_card_update if command == "update" else cmd_card_move
    mock_client = MagicMock()

    with patch("kanban.cli.make_client", return_value=mock_client):
        with pytest.raises(typer.Exit):
            fn(card_id=7, **kwargs)

    mock_client.card_update.assert_not_called()


def test_cli_column_create_omits_position_to_append():
    """Omitted position means append; the server works out the number."""
    from kanban.cli import cmd_column_create

    mock_client = MagicMock()
    mock_client.column_create.return_value = {"id": 3, "position": 2}

    with patch("kanban.cli.make_client", return_value=mock_client):
        cmd_column_create(board_id=1, name="Done", position=None)

    mock_client.column_create.assert_called_once_with(1, "Done", None)


def test_client_column_create_omits_position_when_appending():
    from kanban.client import KanbanClient

    client = KanbanClient(server_url="http://example.test", api_key="k")
    with patch.object(client, "_request", return_value={}) as request:
        client.column_create(1, "Done")

    assert request.call_args.kwargs["json"] == {"board_id": 1, "name": "Done"}
