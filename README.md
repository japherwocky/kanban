# Kanban Board

A full-stack Kanban board application with Python/FastAPI backend, Svelte frontend, and CLI client.

## CLI Installation

Install the CLI to manage your Kanban boards from the command line:

```bash
pip install pkanban
```

## CLI Usage

Configure the CLI to use our hosted service or your self-hosted instance:

```bash
# Use our hosted service (kanban.pearachute.com)
kanban config --url https://kanban.pearachute.com

# Or use a local/self-hosted instance
kanban config --url http://localhost:8000

# Login
kanban login <username> <password>

# List boards
kanban boards

# Create a board
kanban board-create "My Project"

# Show board details
kanban board 1

# Create a card
kanban card-create 1 "To Do" "First task" --position 0
```

### Available Commands

| Command | Description |
|---------|-------------|
| `kanban config --url <url>` | Set the server URL |
| `kanban login <user> <pass>` | Login to the server |
| `kanban logout` | Logout and clear credentials |
| `kanban boards` | List all boards |
| `kanban board-create <name>` | Create a new board |
| `kanban board <id>` | Show board details |
| `kanban board-delete <id>` | Delete a board |
| `kanban column-create <board_id> <name> <position>` | Create a column |
| `kanban column-delete <id>` | Delete a column |
| `kanban card-create <column_id> <title>` | Create a card |
| `kanban card-update <id> <title>` | Update a card |
| `kanban card-delete <id>` | Delete a card |

## 📚 CLI Documentation for Agents

For agents who need to quickly get up to speed with the CLI tool:

- **[CLI Quick Start Guide](docs/cli-quickstart.md)** - Get productive in minutes
- **[CLI Command Reference](docs/cli-reference.md)** - Complete command cheat sheet  
- **[Common Workflows](docs/cli-workflows.md)** - Real-world examples and patterns

## Self-Hosting

### 1. Clone the repository

```bash
git clone https://github.com/pearachute/kanban.git
cd kanban
```

### 2. Set up the virtualenv and install dependencies

```bash
# Create virtualenv (if not already created)
python -m venv venv

# Activate the virtualenv
source venv/bin/activate  # Linux/Mac
# or on Windows:
venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### 3. Initialize the database and create a user

```bash
# From the project root, with venv activated
python manage.py init
python manage.py user-create admin mypassword --admin
```

### 4. Run the server

```bash
# From the project root, with venv activated
python manage.py server
```

The server will start at http://localhost:8000.

The frontend will be built to `backend/static/` and served automatically.

## Development

The virtualenv is at `./venv` in the project root.

```bash
# Activate the virtualenv
source venv/bin/activate  # Linux/Mac
# or on Windows:
venv\Scripts\activate
```

### Running the Server

```bash
# With auto-reload (default)
python manage.py server

# With custom host/port
python manage.py server --host 127.0.0.1 --port 9000

# Disable auto-reload
python manage.py server --no-reload

# Set log level
python manage.py server --log-level debug
```

### Frontend (with hot reload)

```bash
cd frontend
npm run dev
```

### Database Management

```bash
# Initialize database (create all tables)
python manage.py init

# Wipe database (drop all tables and recreate)
python manage.py wipe

# Check database status
python manage.py status

# Create a user
python manage.py user-create <username> <password> [--email EMAIL] [--admin]
```

### Server Options

| Option | Description |
|--------|-------------|
| `--host HOST` | Host to bind to (default: 0.0.0.0) |
| `--port PORT` | Port to bind to (default: 8000) |
| `--reload` | Enable auto-reload (default) |
| `--no-reload` | Disable auto-reload |
| `--log-level LEVEL` | Set logging level (debug, info, warning, error) |

## Multi-Tenant Organizations

See [docs/multi-tenant.md](docs/multi-tenant.md) for details on the organization model, team-based board sharing, and API endpoints.

## API Reference

### Authentication

- `POST /api/token` - Login (returns JWT)

### Boards

- `GET /api/boards` - List accessible boards (owned + shared)
- `POST /api/boards` - Create a new board
- `GET /api/boards/{id}` - Get board with columns and cards
- `POST /api/boards/{id}` - Update board (owner or team member)
- `DELETE /api/boards/{id}` - Delete board (owner only)

### Columns

- `POST /api/columns` - Create column
- `PUT /api/columns/{id}` - Update column
- `DELETE /api/columns/{id}` - Delete column

### Cards

- `POST /api/cards` - Create card
- `PUT /api/cards/{id}` - Update card (including position)
- `DELETE /api/cards/{id}` - Delete card

## Tests

```bash
# Run all tests
python -m pytest backend/tests/
```
