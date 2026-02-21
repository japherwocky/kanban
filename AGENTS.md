# Agent Guidelines for Kanban Project

This document provides guidelines for agentic coding agents working on the Kanban project.

## Project Overview

The Kanban project is a full-stack application with:
- **Backend**: FastAPI server (Python) with Peewee ORM and SQLite
- **CLI**: Python CLI client using typer and rich
- **Frontend**: Svelte (served from backend/static)

## Build, Lint, and Test Commands

### Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install backend dependencies
pip install -r backend/requirements.txt

# Install CLI in editable mode
pip install -e .
```

### Running the Server

```bash
# Development server with auto-reload
python manage.py server

# Custom host/port
python manage.py server --host 127.0.0.1 --port 9000

# Disable auto-reload
python manage.py server --no-reload
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

# Run tests matching a pattern
pytest -k "test_create"

# Run with verbose output
pytest -v

# Run CLI tests specifically
pytest backend/tests/test_cli.py
```

### Type Checking

```bash
# Run pyright (configured in pyrightconfig.json)
pyright

# Or via Python module
python -m pyright
```

## Code Style Guidelines

### General Principles

- Use **absolute imports** (e.g., `from backend.api import api`)
- Add proper type hints for function parameters and return types
- Use docstrings for public functions and classes
- Keep lines under 120 characters when practical

### Import Organization

Organize imports in this order (within each group, use alphabetical order):
1. Standard library imports
2. Third-party imports
3. Local/application imports

```python
# Example import order
import os
import sys
from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.auth import get_current_user
from backend.database import db
from backend.models import User, Board, Column
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Functions/variables | snake_case | `def get_user()`, `board_id` |
| Classes | PascalCase | `class UserResponse` |
| Constants | UPPER_SNAKE_CASE | `MAX_PASSWORD_LENGTH` |
| Files | snake_case | `test_api.py`, `auth.py` |

### Type Annotations

- Use `Optional[X]` instead of `X | None`
- Use explicit return types for all functions
- Prefer built-in collection types (list, dict, set) over typing classes

```python
# Good
def get_board(board_id: int) -> Optional[Board]:
    ...

def list_boards(user: User) -> list[dict]:
    ...

# Avoid
def get_board(board_id):
    ...

def list_boards(user):
    ...
```

### Pydantic Models

Use Pydantic v2 style with `model_config`:

```python
class BoardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    created_at: datetime
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

```python
# Good
raise HTTPException(status_code=404, detail="Board not found")
raise HTTPException(status_code=403, detail="Not authorized")

# Avoid bare raises or generic errors
raise Exception("Error")
```

### CLI Commands

- Use typer for CLI framework
- Use rich for formatted output
- Follow existing command structure patterns
- Use `typer.Option` and `typer.Argument` appropriately

```python
@app.command("create")
def cmd_board_create(name: str = typer.Argument(..., help="Board name")):
    """Create a new board."""
    client = make_client()
    result = client.board_create(name)
    rprint(f"Board created with [green]id={result['id']}[/green]")
```

### Test Patterns

Follow the patterns in `backend/tests/`:

```python
# Use fixtures from conftest.py
def test_create_board(client, auth_headers, test_user):
    response = client.post(
        "/api/boards",
        json={"name": "Test Board"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    
# Use auth_headers fixture for authenticated requests
@pytest.fixture
def auth_headers(test_user):
    from backend.auth import create_access_token
    token = create_access_token(data={"sub": test_user.id, "username": test_user.username})
    return {"Authorization": f"Bearer {token}"}
```

### API Route Patterns

- Group related endpoints
- Use dependency injection for authentication
- Return Pydantic models with proper response_model
- Use appropriate HTTP methods (GET, POST, PUT, DELETE)

```python
@api.post("/boards", response_model=dict)
async def create_board(
    board_data: BoardCreate, 
    current_user: User = Depends(get_current_user_or_api_key)
):
    with db.atomic():
        board = Board.create_with_columns(...)
    return {"id": board.id, ...}
```

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

## Key Dependencies

- **Backend**: fastapi, uvicorn, peewee, pydantic, python-jose, bcrypt
- **CLI**: typer, rich, requests, pyyaml
- **Testing**: pytest, pytest-asyncio, httpx
- **Type checking**: pyright

## Common Tasks

### Adding a New API Endpoint

1. Add request/response models in `backend/api.py`
2. Add route handler function
3. Add permission checks
4. Add test in appropriate test file

### Adding a New CLI Command

1. Add command function in `kanban/cli.py`
2. Use `make_client()` for authenticated commands
3. Use `typer.Option` and `typer.Argument` for parameters
4. Use `rprint()` from rich for output

### Adding a Database Model

1. Add model class in `backend/models.py`
2. Add to tables list in `manage.py`
3. Run `python manage.py init` or `python manage.py wipe`
4. Add test fixtures if needed
