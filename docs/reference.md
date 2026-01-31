# CLI Command Reference Cheat Sheet

Complete reference for all Kanban CLI commands. Perfect for quick lookups during agent operations.

> **Detailed Pages:** Each command group has a dedicated page with examples:
> - [All Commands Index](/docs/commands) - Navigable command list
> - [Authentication](/docs/commands/config) - config, login, logout
> - [Boards](/docs/commands/boards) - boards, board-create, board, board-delete, share
> - [Columns](/docs/commands/column) - column management
> - [Cards](/docs/commands/card) - card management
> - [Organizations](/docs/commands/org) - org management
> - [Teams](/docs/commands/team) - team management
> - [API Keys](/docs/commands/apikey) - apikey management

## 🔐 Authentication & Configuration

| Command | Usage | Description |
|---------|-------|-------------|
| `kanban config` | `kanban config [--url URL]` | Show or set server URL |
| `kanban login` | `kanban login <user> --password <pass>` | Login to server |
| `kanban logout` | `kanban logout` | Logout and clear credentials |

## 📋 Board Management

| Command | Usage | Description |
|---------|-------|-------------|
| `kanban boards` | `kanban boards` | List all accessible boards |
| `kanban board-create` | `kanban board-create <name>` | Create new board |
| `kanban board` | `kanban board <board-id>` | Show board details |
| `kanban board-delete` | `kanban board-delete <board-id>` | Delete board |
| `kanban share` | `kanban share <board-id> <team-id\|private>` | Share with team or make private |

## 📊 Column Management

| Command | Usage | Description |
|---------|-------|-------------|
| `kanban column-create` | `kanban column-create <board-id> <name> <position>` | Create column |
| `kanban column-delete` | `kanban column-delete <column-id>` | Delete column |

## 🃏 Card Management

| Command | Usage | Description |
|---------|-------|-------------|
| `kanban card-create` | `kanban card-create <column-id> <title> [--description TEXT] [--position NUM]` | Create card |
| `kanban card-update` | `kanban card-update <card-id> <title> [--description TEXT] [--position NUM] [--column NUM]` | Update card |
| `kanban card-delete` | `kanban card-delete <card-id>` | Delete card |

## 🏢 Organization Commands (`kanban org`)

| Sub-command | Usage | Description |
|-------------|-------|-------------|
| `kanban org list` | `kanban org list` | List all organizations |
| `kanban org create` | `kanban org create <name>` | Create organization |
| `kanban org get` | `kanban org get <org-id>` | Show organization details |
| `kanban org members` | `kanban org members <org-id>` | List organization members |
| `kanban org member-add` | `kanban org member-add <org-id> <username>` | Add member |
| `kanban org member-remove` | `kanban org member-remove <org-id> <user-id>` | Remove member |

## 👥 Team Commands (`kanban team`)

| Sub-command | Usage | Description |
|-------------|-------|-------------|
| `kanban team list` | `kanban team list --org-id <org-id>` | List teams in org |
| `kanban team create` | `kanban team create <org-id> <name>` | Create team |
| `kanban team get` | `kanban team get <team-id>` | Show team details |
| `kanban team members` | `kanban team members <team-id>` | List team members |
| `kanban team member-add` | `kanban team member-add <team-id> <username>` | Add member |
| `kanban team member-remove` | `kanban team member-remove <team-id> <user-id>` | Remove member |

## 🔑 API Key Commands (`kanban apikey`)

| Sub-command | Usage | Description |
|-------------|-------|-------------|
| `kanban apikey list` | `kanban apikey list` | List all API keys |
| `kanban apikey create` | `kanban apikey create <name>` | Create new API key |
| `kanban apikey revoke` | `kanban apikey revoke <key-id>` | Revoke/deactivate an API key |
| `kanban apikey activate` | `kanban apikey activate <key-id>` | Reactivate a deactivated API key |
| `kanban apikey use` | `kanban apikey use <key> <command>` | Run command using an API key |

## 🎯 Common Parameter Patterns

### IDs are always numbers
- Board IDs: `1`, `2`, `3`
- Column IDs: `1`, `2`, `3`  
- Card IDs: `1`, `2`, `3`
- Organization IDs: `1`, `2`, `3`
- Team IDs: `1`, `2`, `3`
- User IDs: `1`, `2`, `3`

### Position is always 0-based
- Position 0 = first position
- Position 1 = second position
- etc.

### Required vs Optional Parameters
```bash
# Required parameters (no brackets)
kanban board-create "Board Name"

# Optional parameters (shown in brackets)
kanban card-create 1 "Title" --description "Optional" --position 0
```

## 🚀 Quick Command Sequences

### New Board Setup
```bash
kanban board-create "Project Name"
kanban board <new-board-id>  # Get default columns
kanban column-create <board-id> "To Do" 0
kanban column-create <board-id> "Doing" 1
kanban column-create <board-id> "Done" 2
```

### Team Setup
```bash
kanban org create "Company"
kanban team create <org-id> "Dev Team"
kanban org member-add <org-id> <username>
kanban team member-add <team-id> <username>
```

### Card Workflow
```bash
kanban card-create <todo-column-id> "New Task" --position 0
kanban card-update <card-id> "Updated Task" --column <doing-column-id> --position 0
kanban card-update <card-id> "Completed Task" --column <done-column-id> --position 0
```

## 🔧 Help System

Get help for any command:
```bash
kanban --help                    # All commands
kanban board-create --help       # Specific command
kanban org --help               # Organization sub-commands
kanban team --help              # Team sub-commands
```

## ⚡ Pro Tips

1. **Always run `kanban boards` first** to see available board IDs
2. **Use `kanban board <id>`** to see column IDs for card operations
3. **Team commands require `--org-id`** flag except for `team get`
4. **Board sharing overwrites** existing sharing settings
5. **Positions are per-column** for cards, per-board for columns