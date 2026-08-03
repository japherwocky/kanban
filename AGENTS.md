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

Server-side:

- `RESEND_API_KEY`: Resend key for outbound email. Unset, mail is printed to
  stderr instead of sent — which is how local development works without a key.
- `RESEND_FROM`: Sender address (default `Kanban <noreply@pearachute.com>`).
  The domain must be verified in Resend, and a subdomain counts as a separate
  domain there — hence the apex, which the main pearachute.com site also sends
  from. Sending from an unverified domain fails every time, silently as far as
  the user is concerned: signup still succeeds and the rejection only appears
  in the service log.
- `PUBLIC_BASE_URL`: Origin used to build links in email (default
  `https://kanban.pearachute.com`).

### Signup and Email Verification

Signup is self-serve and open: `POST /api/signup` takes `{username, email,
password}` and creates the account with `email_verified=False`, then emails a
link. `POST /api/token` returns **403 "Email not verified"** until
`POST /api/verify-email` consumes that token, which also returns a JWT so the
user lands logged in.

Two things to keep in mind when touching this:

- `User.create_user()` defaults to `email_verified=True`. Admin- and
  CLI-created accounts are trusted; only the signup endpoint passes False.
  Flipping that default would make `manage.py user-create` produce accounts
  that cannot log in.
- Signup grants no organization access whatsoever. Joining an existing org
  happens only via an owner calling `POST /organizations/{id}/members` or via
  an `OrganizationInvite` token. Don't add an org field to signup.

There is no rate limiting anywhere in the stack. The 60-second per-account
resend cooldown is the only brake on outbound verification mail.

Deploying this needs no manual migration step — `sys/scripts/deploy.sh` now runs
`manage.py migrate` before restarting the service. See Database Migrations below.

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

# Apply pending migrations
python manage.py migrate

# Show what is applied and what is pending, without running anything
python manage.py migrate --list
```

### Database Migrations

Migrations live in `backend/migrations/` and run under **peewee-migrate**.
`sys/scripts/deploy.sh` calls `manage.py migrate` on every deploy, before the
service restarts, and a failure aborts the deploy — the service keeps serving
the old code rather than starting against a schema it does not match.

Applied migrations are recorded in a `migratehistory` table, so running the
command repeatedly is cheap and safe.

Writing a new one — name it `NNN_description.py` (the three-digit prefix is how
peewee-migrate finds and orders them) and define:

```python
def migrate(migrator, database, *, fake=False):
    ...

def rollback(migrator, database, *, fake=False):
    ...
```

Two conventions worth keeping:

- **Make it idempotent.** Check before you alter. Production applied migration
  001 by hand years before there was a history table, and a fresh install gets
  most columns from `create_tables()` in `init_db()` — so a migration routinely
  meets a database that already has some of its changes.
- **Match peewee's index names.** `create_tables()` names the index for
  `email = CharField(unique=True)` as `user_email`. A migration that invents its
  own name leaves fresh installs and migrated databases with different schemas.

`init_db()` still creates *new tables* from the models on startup, so a
migration only needs to handle columns, indexes and data.

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