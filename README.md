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

### 3. Initialize the database

```bash
# From the project root, with venv activated
python -m backend.manage init
```

### 4. Create a user

```bash
# From the project root, with venv activated
python backend/create_user.py <username> <password> [--email EMAIL] [--admin]
```

### 5. Run the backend

```bash
# From the project root, with venv activated
uvicorn backend.main:app --reload
```

### 6. Build and run the frontend

```bash
cd frontend
npm run build
```

The frontend will be built to `backend/static/` and served automatically.

## Development

The virtualenv is at `./venv` in the project root.

```bash
# Activate the virtualenv
source venv/bin/activate  # Linux/Mac
# or on Windows:
venv\Scripts\activate

# Run the backend (from project root)
uvicorn backend.main:app --reload
```

### Frontend (with hot reload)

```bash
cd frontend
npm run dev
```

### Database Management

```bash
# Initialize database (create all tables)
python -m backend.manage init

# Wipe database (drop all tables and recreate)
python -m backend.manage wipe

# Check database status
python -m backend.manage status
```

## Multi-Tenant Organizations

The application supports multi-tenant organizations with team-based board sharing.

### Organization Model

- **Organizations** group users and teams
- **Organization Members** have roles: `owner`, `admin`, or `member`
- **Teams** are groups of users within an organization
- **Team Members** have roles: `admin` or `member`

### Board Sharing

- Boards are always owned by an individual user
- By default, boards are private (only the owner can access)
- Boards can be shared with a single team for collaboration
- Shared boards: owner + all team members can edit; only owner can delete or change sharing

### Organization API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/organizations` | Create organization (auto-creates "Administrators" team) |
| `GET` | `/api/organizations` | List user's organizations |
| `GET` | `/api/organizations/{id}` | Get organization details |
| `PUT` | `/api/organizations/{id}` | Update organization (owner/admin only) |
| `POST` | `/api/organizations/{id}/members` | Add member |
| `GET` | `/api/organizations/{id}/members` | List members |
| `PUT` | `/api/organizations/{id}/members/{user_id}` | Update member role |
| `DELETE` | `/api/organizations/{id}/members/{user_id}` | Remove member |

### Team API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/organizations/{id}/teams` | Create team |
| `GET` | `/api/organizations/{id}/teams` | List teams |
| `PUT` | `/api/teams/{id}` | Update team (team admin only) |
| `DELETE` | `/api/teams/{id}` | Delete team (org admin only) |
| `POST` | `/api/teams/{id}/members` | Add team member |
| `GET` | `/api/teams/{id}/members` | List team members |
| `PUT` | `/api/teams/{id}/members/{user_id}` | Update team member role |
| `DELETE` | `/api/teams/{id}/members/{user_id}` | Remove team member |

### Board Sharing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/boards/{id}/share` | Share board with a team (owner only) |

Request body: `{"team_id": null}` to make private, `{"team_id": <team_id>}` to share.

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
