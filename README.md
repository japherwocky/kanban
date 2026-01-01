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

### 2. Create a user

```bash
# Activate the virtualenv (located at ./venv in the project root)
source venv/bin/activate  # Linux/Mac
# or on Windows:
venv\Scripts\activate

# Install dependencies and create a user
pip install -r backend/requirements.txt
cd backend
python create_user.py <username> <password>
```

### 3. Run the backend

```bash
# From the project root, with venv activated
uvicorn backend.main:app --reload
```

### 4. Build and run the frontend

```bash
cd frontend
npm install
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

## API

- `POST /api/token` - Login (returns JWT)
- `GET /api/boards` - List user's boards
- `POST /api/boards` - Create a new board
- `GET /api/boards/{id}` - Get board with columns and cards
- `POST /api/boards/{id}` - Update board
- `DELETE /api/boards/{id}` - Delete board
- `POST /api/columns` - Create column
- `PUT /api/columns/{id}` - Update column
- `DELETE /api/columns/{id}` - Delete column
- `POST /api/cards` - Create card
- `PUT /api/cards/{id}` - Update card (including position)
- `DELETE /api/cards/{id}` - Delete card

## Tests

```bash
cd backend
pytest
```
