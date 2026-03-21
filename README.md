# pkanban

A command-line tool for managing Kanban boards. (The "p" is silent, like in "pneumonia".)

Most users will connect to our hosted service at [kanban.pearachute.com](https://kanban.pearachute.com). If you want to run your own server, see the Self-Hosting section below.

## Quick Start

```bash
pip install pkanban
```

Configure the CLI to connect to the hosted service:

```bash
kanban config --url https://kanban.pearachute.com
kanban login <username> --password <password>
```

That's it! You can now manage your boards from the command line.

## Common Commands

```bash
# List your boards
kanban board list

# Create a new board
kanban board create "My Project"

# View a board with its columns and cards
kanban board get 1

# Add a column
kanban column create 1 "To Do" 0

# Add a card
kanban card create 1 "First task" --description "Getting started"

# Share a board with a team
kanban share 1 <team-id>
```

## API Keys

For automation, CI/CD, or giving access to agents, use API keys instead of passwords:

```bash
# Create a key (shown only once!)
kanban apikey create "CI Agent"

# Use it
kanban --api-key kanban_abc123... board list

# Or set it as an environment variable
export KANBAN_API_KEY=kanban_abc123...
kanban board list
```

API keys can be revoked and reactivated at any time. They're stored securely (bcrypt-hashed) and track their last usage.

## Command Reference

| Command | Description |
|---------|-------------|
| `kanban config [--url URL]` | Show or set server URL |
| `kanban login <user> --password <pass>` | Login to the server |
| `kanban logout` | Logout and clear credentials |
| `kanban --api-key <key>` | Use API key for authentication |
| `kanban apikey create <name>` | Generate a new API key |
| `kanban apikey list` | List your API keys |
| `kanban apikey revoke <id>` | Revoke an API key |
| `kanban apikey activate <id>` | Reactivate a revoked key |
| `kanban board list` | List all boards |
| `kanban board create <name>` | Create a new board |
| `kanban board get <id>` | Show board details |
| `kanban board delete <id>` | Delete a board |
| `kanban board update <id> <name>` | Update board name |
| `kanban share <board_id> <team_id\|private>` | Share board or make private |
| `kanban column create <board_id> <name> <position>` | Create a column |
| `kanban column delete <id>` | Delete a column |
| `kanban card create <column_id> <title> [options]` | Create a card |
| `kanban card update <id> <title> [options]` | Update a card |
| `kanban card delete <id>` | Delete a card |
| `kanban org list` | List all organizations |
| `kanban org create <name>` | Create an organization |
| `kanban org get <org-id>` | Show organization details |
| `kanban org members <org-id>` | List organization members |
| `kanban org member-add <org-id> <username>` | Add member to organization |
| `kanban org member-remove <org-id> <user-id>` | Remove member |
| `kanban team list --org-id <org-id>` | List teams in organization |
| `kanban team create <org-id> <name>` | Create a new team |
| `kanban team get <team-id>` | Show team details |
| `kanban team members <team-id>` | List team members |
| `kanban team member-add <team-id> <username>` | Add member to team |
| `kanban team member-remove <team-id> <user-id>` | Remove member from team |

## Self-Hosting

Want to run your own server? Here's how:

### 1. Clone and setup

```bash
git clone https://github.com/pearachute/kanban.git
cd kanban
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2. Initialize and run

```bash
python manage.py init
python manage.py user-create admin mypassword --admin
python manage.py server
```

The server runs at http://localhost:8000 by default.

### 3. Connect the CLI

```bash
kanban config --url http://localhost:8000
kanban login admin --password mypassword
```

## Development

```bash
# Run the server with auto-reload
python manage.py server

# Run frontend dev server (hot reload)
cd frontend && npm run dev

# Run tests
python -m pytest backend/tests/
```

### Database commands

```bash
python manage.py init          # Create tables
python manage.py wipe          # Drop and recreate tables
python manage.py status        # Check database status
python manage.py user-create <user> <pass> [--admin]
```

## API Reference

The backend exposes a REST API at `/api/`:

**Authentication**
- `POST /api/token` - Login (returns JWT)
- `X-API-Key` header - Alternative auth via API key

**API Keys**
- `GET /api/api-keys` - List your keys
- `POST /api/api-keys` - Create a key
- `DELETE /api/api-keys/{id}` - Revoke a key
- `POST /api/api-keys/{id}/activate` - Reactivate a key

**Boards**
- `GET /api/boards` - List accessible boards
- `POST /api/boards` - Create a board
- `GET /api/boards/{id}` - Get board details
- `POST /api/boards/{id}` - Update board
- `DELETE /api/boards/{id}` - Delete board

**Columns**
- `POST /api/columns` - Create column
- `PUT /api/columns/{id}` - Update column
- `DELETE /api/columns/{id}` - Delete column

**Cards**
- `POST /api/cards` - Create card
- `PUT /api/cards/{id}` - Update card
- `DELETE /api/cards/{id}` - Delete card

For multi-tenant organization details, see [docs/multi-tenant.md](docs/multi-tenant.md).