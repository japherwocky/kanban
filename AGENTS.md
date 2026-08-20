# AGENTS.md

**This is the file to edit.** AGENTS.md is the cross-agent standard and is read
by every agent that works here; CLAUDE.md is a four-line shim that imports it.
Guidance written only into CLAUDE.md is invisible to all but one agent, and the
two then drift -- so put it here, and leave CLAUDE.md alone.

## Read this first

Rules whose violation produces no error, no failing test, and no failing build
-- just work that quietly did nothing. Each one has already cost this repo real
time. Nothing else belongs in this section; if CI or a test catches it, it does
not need a slot here.

- **`svelte-dnd-action` is an action: `use:dndzone={...}`, never
  `dndzone={...}`.** Written as a bare attribute it compiles, renders, deploys
  and does nothing at all. Drag-and-drop was dead from f75f15a until PR #40 --
  through three commits (b97c8d3, 0a04dac, f0f145f) fixing logic that was never
  reached. `BoardView.test.js` guards it now; the rule is here because the
  failure mode is invisible.

- **Never load fonts with `@import` from a CSS file.** An `@import` in
  `theme.css` is flattened into `app.css` after Tailwind has emitted its
  `@layer` statements, which makes it invalid -- and postcss drops it from the
  build without failing it. Web fonts never loaded at all until PR #36, and
  every page rendered in the system fallback. Use `<link>` in `index.html`.

- **Svelte trims literal whitespace at element and `{#if}` boundaries.** A space
  written in the markup between a value and an adjacent tag simply vanishes, so
  `{title} <span>{badge}</span>` renders as `Edit Card#42`. Interpolate the
  space when it matters -- see the heading in `Modal.svelte`.

- **Sending mail from an unverified domain fails silently.** `RESEND_FROM` must
  name a domain verified in Resend, and a subdomain counts as a separate domain
  there -- hence the apex. Get it wrong and signup still returns success, the
  user simply never receives the verification mail; the rejection appears only
  in the service log.

- **A 401 is not an empty board.** `kanban board get 1` answering
  `Not authenticated` means the session ended, not that the board has no cards.
  Sessions renew while in use, so this takes a day away or a login older than
  30 days -- both of which happen. Re-authenticate before concluding anything
  about a board's contents.

- **Run the CLI from the venv: `venv/Scripts/kanban.exe`.** Plain `kanban` is
  not on PATH unless the venv is activated, and if `pkanban` happens to be
  installed globally it answers instead -- a different version, reading a
  different config, with nothing to indicate the substitution.

Caught elsewhere, so deliberately not repeated above: an undefined
`var(--token)` resolves to `unset` and blanks whatever it styled
(`scripts/check_css_tokens.py`), and a `package-lock.json` regenerated in place
is pruned to one platform and breaks `npm ci` everywhere else (CI's lockfile
check; the recipe is in `frontend/LOCKFILE.md`).

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
- **Auth**: a JWT token or an API key, stored in `~/.kanban.yaml`

JWTs expire; API keys do not. A session in regular use now renews itself --
the server returns a replacement on `X-Renewed-Token` once a token is within
12 hours of expiring, and the CLI saves it to `~/.kanban.yaml`. More than 24
hours between commands still expires the session, as does a login older than
30 days. A `401 Not authenticated` means re-authenticate: `kanban login`, or
use an API key as below.

### Running the CLI from this repo

The `kanban` command is not on the PATH unless the venv is activated. From
this repo root, call the venv binary directly:

```bash
# Windows
venv/Scripts/kanban.exe --help

# macOS/Linux
venv/bin/kanban --help
```

The CLI is installed in editable mode (`pip install -e .`), so changes under
`kanban/` take effect immediately. Activating the venv
(`venv/Scripts/activate` on Windows, `source venv/bin/activate` elsewhere)
puts plain `kanban` on the PATH.

### Authenticating with an API key

`--api-key <key>` authenticates a single command only. It goes through the
in-memory runtime key and never touches the config file, so it is safe for
per-command use by agents and scripts:

```bash
venv/Scripts/kanban.exe --api-key kanban_1-<KEY> board list --json
```

The project's key is the `opencode` key (see `kanban apikey list`). Do not
commit it to this repo — the repo is public. To use it for every command
without retyping it, save it once with `kanban apikey save kanban_1-<KEY>`.

### Project Board

The **Dev** board (id=1) is the board for this project. Columns:

- **Todo** (id 4) — backlog
- **In Progress** (id 5) — being worked on now
- **Done** (id 6) — completed

### Useful Commands
```bash
kanban board list                    # List all boards
kanban board get 1                    # Show Dev board details
kanban board get <id>                 # Show board with columns & cards
kanban card get <id>                  # Read one card's full contents
```

### Scripting the CLI

Pass `--json` (or set `KANBAN_OUTPUT=json`) and every command prints the raw
API response instead of formatted text. Use it rather than parsing the human
output — the prose is not an interface, and a reworded string silently breaks
anything that regexes it.

```bash
kanban column create 1 Todo 0 --json | jq -r .id
kanban board get 1 --json | jq '.columns[].cards[] | {id, title, description}'
```

The flag works before or after the subcommand. In JSON mode stdout holds only
the response; errors go to stderr as `{"error": ..., "status": ...}` alongside
a non-zero exit code, so stdout is always safe to pipe into a parser.

`kanban card get <id>` reads one card, including its description, the comments
and which board/column it sits on:

```bash
kanban card get 92 --json | jq -r .description
```

Two things that used to make seeding a board fiddly are gone: `column create`
appends when you omit the position, and `card move <id> --column <n>` moves a
card without retyping its title (on `card update`, anything you don't pass is
left unchanged).

An unmatched `/api/...` path returns a JSON 404. The SPA catch-all in
`backend/main.py` is scoped to non-API paths for exactly this reason: it used
to answer 200 with index.html for anything it did not recognise, so a missing
endpoint was indistinguishable from a working one and `response.json()` failed
with a decode error rather than surfacing the 404. Keep that guard in place
when touching the fallback.

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
### Deploying systemd and nginx config

`deploy.sh` installs `sys/systemd/kanban.service` itself when it differs from
`/etc/systemd/system/kanban.service`, then `daemon-reload`s before restarting.
On an unchanged unit it is a no-op and needs no sudo.

This needs three narrow sudoers rules, written by `install.sh`:

```
kanban ALL=(ALL) NOPASSWD: /bin/systemctl restart kanban
kanban ALL=(ALL) NOPASSWD: /bin/systemctl daemon-reload
kanban ALL=(ALL) NOPASSWD: /bin/cp /opt/kanban/sys/systemd/kanban.service /etc/systemd/system/kanban.service
```

If they are missing, a deploy carrying a unit change **fails** rather than
restarting onto the stale unit. That is deliberate. Before this existed, a unit
edit reached the repo and the box but never the running service and said
nothing about it — `EnvironmentFile=-/opt/kanban/.env` sat unapplied long
enough that `RESEND_API_KEY` was set correctly and still ignored, so signup
returned 201 and sent no mail.

Two things that make this class of bug hard to see:

- `systemctl show kanban --property=Environment` does **not** expand
  `EnvironmentFile` contents, so it looks identical whether the file is read or
  not. Use `--property=EnvironmentFiles`, `systemctl cat kanban`, or read
  `/proc/$(systemctl show kanban --property=MainPID --value)/environ`.
- The leading `-` in `EnvironmentFile=-` makes a missing or unread file
  non-fatal by design, so nothing complains.

`sys/nginx/kanban.pearachute.com.conf` is still installed by hand — the deploy
does not touch it.
