
## Project Overview

The Kanban project is a full-stack application with:
- **Backend**: FastAPI server (Python) with Peewee ORM and SQLite
- **CLI**: Python CLI client using typer and rich
- **Frontend**: Svelte (served from backend/static)

## Build, Lint, and Test Commands

### Setup
the virtualenv probably already exists at ./venv

please use it, and create a new one if necessary.

# Install CLI in editable mode
pip install -e .

then run it like `kanban --help`


### Running the Server

# Development server with auto-reload
python manage.py server

# Custom host/port
python manage.py server --host 127.0.0.1 --port 9000

# Disable auto-reload
python manage.py server --no-reload

### Database Management

# Initialize database
python manage.py init

# Wipe database (destructive)
python manage.py wipe

# Create a user
python manage.py user-create <username> <password> [--email EMAIL] [--admin]

# Check database status
python manage.py status


### Running Tests

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



### Database Patterns

- Use Peewee ORM with proper relationships
- Use `get_or_none()` for lookups that may fail
- Wrap multiple writes in `db.atomic()` transaction
- Use fixtures from `conftest.py` for tests

# Good pattern for lookups
board = Board.get_or_none(Board.id == board_id)
if not board:
    raise HTTPException(status_code=404, detail="Board not found")

# Good pattern for transactions
with db.atomic():
    column.delete_instance()
    board.delete_instance()

### Error Handling

- Use FastAPI's `HTTPException` with appropriate status codes
- Return meaningful error messages
- Use consistent error response format


### CLI Commands

- Use typer for CLI framework
- Use rich for formatted output
- Follow existing command structure patterns
- Use `typer.Option` and `typer.Argument` appropriately


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
├── kanban/              # CLI client package
│   ├── cli.py          # CLI commands
│   ├── client.py       # API client
│   └── config.py       # Configuration
├── frontend/           # Svelte frontend
├── docs/               # Documentation
├── manage.py           # Server management
├── pyproject.toml      # Project config
└── pyrightconfig.json  # Type checking config
```
