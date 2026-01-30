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
kanban login <username> --password <password>

# Or use an API key (for agents/CI)
kanban --api-key <key> boards

# List boards
kanban boards

# Create a board
kanban board-create "My Project"

# Show board details
kanban board 1

# Create a card
kanban card-create 1 "To Do" "First task" --position 0

# Share a board with a team
kanban share 1 <team-id>
# Or make a board private
kanban share 1 private

# Organization management
kanban org create "My Company"
kanban org get 1

# Team management
kanban team create 1 "Engineering"
kanban team list --org-id 1
```

### Available Commands

| Command | Description |
|---------|-------------|
| `kanban config [--url URL]` | Show or set server URL |
| `kanban login <user> --password <pass>` | Login to the server |
| `kanban logout` | Logout and clear credentials |
| `kanban --api-key <key>` | Use API key for authentication (global option) |
| `kanban apikey create <name>` | Generate a new API key |
| `kanban apikey list` | List your API keys |
| `kanban apikey revoke <id>` | Revoke (deactivate) an API key |
| `kanban apikey activate <id>` | Reactivate a deactivated API key |
| `kanban boards` | List all boards |
| `kanban board-create <name>` | Create a new board |
| `kanban board <id>` | Show board details |
| `kanban board-delete <id>` | Delete a board |
| `kanban share <board_id> <team_id\|private>` | Share board with team or make private |
| `kanban column-create <board_id> <name> <position>` | Create a column |
| `kanban column-delete <id>` | Delete a column |
| `kanban card-create <column_id> <title> [--description TEXT] [--position NUM]` | Create a card |
| `kanban card-update <id> <title> [--description TEXT] [--position NUM] [--column NUM]` | Update a card |
| `kanban card-delete <id>` | Delete a card |
| `kanban org list` | List all organizations |
| `kanban org create <name>` | Create a new organization |
| `kanban org get <org-id>` | Show organization details |
| `kanban org members <org-id>` | List organization members |
| `kanban org member-add <org-id> <username>` | Add member to organization |
| `kanban org member-remove <org-id> <user-id>` | Remove member from organization |
| `kanban team list --org-id <org-id>` | List teams in organization |
| `kanban team create <org-id> <name>` | Create a new team |
| `kanban team get <team-id>` | Show team details |
| `kanban team members <team-id>` | List team members |
| `kanban team member-add <team-id> <username>` | Add member to team |
| `kanban team member-remove <team-id> <user-id>` | Remove member from team |

## 📚 CLI Documentation for Agents

For agents who need to quickly get up to speed with the CLI tool:

- **[CLI Quick Start Guide](docs/cli-quickstart.md)** - Get productive in minutes
- **[CLI Command Reference](docs/cli-reference.md)** - Complete command cheat sheet
- **[Common Workflows](docs/cli-workflows.md)** - Real-world examples and patterns

## 🔑 API Keys for Agents

Instead of sharing passwords, users can generate one-off API keys for agents and CI/CD pipelines:

```bash
# Generate an API key (shown only once - save it securely!)
kanban apikey create "CI Agent"

# Use the API key for any command
kanban --api-key kanban_abc123... boards

# Or set it as default
export KANBAN_API_KEY=kanban_abc123...
kanban boards
```

### API Key Features

- **Secure**: API keys are bcrypt-hashed in the database (like passwords)
- **Revokable**: Deactivate or reactivate keys at any time
- **Identifiable**: Each key has a prefix for identification in logs
- **Trackable**: Last used timestamp recorded for each key

### Security Notes

- API keys are shown only once at creation time - copy and store securely
- Use environment variables or secure secret management for CI/CD
- Rotate keys periodically and revoke compromised keys

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
- `X-API-Key` header - Use API key for authentication (alternative to Bearer token)

### API Keys

- `GET /api/api-keys` - List your API keys
- `POST /api/api-keys` - Create a new API key (returns key once)
- `DELETE /api/api-keys/{id}` - Revoke (deactivate) an API key
- `POST /api/api-keys/{id}/activate` - Reactivate a deactivated API key

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
