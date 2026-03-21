## Project Overview

The Kanban project is a full-stack application with:
- **Backend**: FastAPI server (Python) with Peewee ORM and SQLite
- **CLI**: Python CLI client using typer and rich (published as `pkanban` on PyPI)
- **Frontend**: Svelte (served from backend/static)
- **Features**: Multi-tenancy with organizations, teams, API keys, and board sharing

## Remote Configuration

This project uses a remote Kanban server at **kanban.pearachute.com**.

### Config
The CLI is configured to connect to:
- **Server**: https://kanban.pearachute.com
- **Auth**: API key (stored in `~/.kanban.yaml`)

### Project Board
The **Dev** board (id=1) is the board for this project.

### Useful Commands
```bash
kanban board list                    # List all boards
kanban board get 1                    # Show Dev board details
kanban board get <id>                 # Show board with columns & cards
```

## Build, Lint, and Test Commands

### Setup

The virtualenv probably already exists at `./venv`. Please use it, or create a new one if necessary.

```bash
# Install CLI in editable mode
pip install -e .

# Run it
kanban --help
```

### Environment Variables

- `KANBAN_CONFIG_PATH`: Path to config file (default: ~/.kanban.yaml)
- `KANBAN_API_KEY`: Default API key for authentication

### Running the Server

```bash
# Development server with auto-reload (default port 8080)
python manage.py server

# Custom host/port
python manage.py server --host 127.0.0.1 --port 9000

# Disable auto-reload
python manage.py server --no-reload

# Set log level
python manage.py server --log-level debug
```

### Database Management

```bash
# Initialize database
python manage.py init

# Wipe database (destructive)
python manage.py wipe

# Create a user
python manage.py user-create <username> <password> [--email EMAIL] [--admin]

# Check database status
python manage.py status
```

### Running Tests

```bash
# Run all backend tests
pytest

# Run all tests in backend/tests/
python -m pytest backend/tests/

# Run a single test file
pytest backend/tests/test_api.py

# Run a single test function
pytest backend/tests/test_api.py::test_login_success

# Run CLI tests specifically
pytest backend/tests/test_cli.py
```

### Database Patterns

- Use Peewee ORM with proper relationships
- Use `get_or_none()` for lookups that may fail
- Wrap multiple writes in `db.atomic()` transaction
- Use fixtures from `conftest.py` for tests

```python
# Good pattern for lookups
board = Board.get_or_none(Board.id == board_id)
if not board:
    raise HTTPException(status_code=404, detail="Board not found")

# Good pattern for transactions
with db.atomic():
    column.delete_instance()
    board.delete_instance()
```

### Error Handling

- Use FastAPI's `HTTPException` with appropriate status codes
- Return meaningful error messages
- Use consistent error response format

### CLI Commands

- Use typer for CLI framework
- Use rich for formatted output
- Follow existing command structure patterns
- Use `typer.Option` and `typer.Argument` appropriately

## PyPI Publishing

The CLI package is published as **pkanban** on PyPI. Publishing is automated via GitHub Actions.

### Publishing a New Version

1. Update version in both files:
   - `pyproject.toml`: `version = "X.Y.Z"`
   - `kanban/__init__.py`: `__version__ = "X.Y.Z"`

2. Commit and push:
   ```bash
   git add -A && git commit -m "Bump version to X.Y.Z"
   git push
   ```

3. Create and push a tag:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. GitHub Actions handles the rest:
   - Builds wheel and source distribution
   - Publishes to PyPI (using trusted publishing)
   - Creates a GitHub Release with notes

### Manual Publishing (if needed)

```bash
# Build
python -m build

# Upload (requires .pypirc or API token)
twine upload dist/*
```

### Files Involved

- `.github/workflows/publish-pypi.yml` - GitHub Actions workflow
- `pyproject.toml` - Package metadata and version
- `kanban/__init__.py` - Package version (must match pyproject.toml)
- `~/.pypirc` - PyPI credentials (for manual uploads)

## Project Structure

```
kanban/
├── backend/              # FastAPI backend
│   ├── api.py           # API routes
│   ├── auth.py          # Authentication
│   ├── database.py      # Database connection
│   ├── models.py        # Peewee models
│   ├── main.py          # FastAPI app
│   ├── conftest.py      # Test fixtures
│   ├── tests/           # Test files
│   │   ├── test_api.py
│   │   ├── test_cli.py
│   │   └── ...
│   └── static/          # Built frontend
├── kanban/              # CLI client package (published as pkanban)
│   ├── __init__.py      # Package init, version
│   ├── __main__.py      # Entry point for `python -m kanban`
│   ├── cli.py           # CLI commands
│   ├── client.py        # API client
│   └── config.py        # Configuration
├── frontend/            # Svelte frontend
├── docs/                # Documentation
├── manage.py            # Server management
├── pyproject.toml       # Project config & package metadata
└── pyrightconfig.json   # Type checking config
```