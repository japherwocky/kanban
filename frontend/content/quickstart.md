# CLI Quick Start Guide for Agents

This guide helps agents get up to speed quickly with the Kanban CLI tool for managing boards, organizations, and teams.

## 🚀 Quick Setup

### 1. Installation
```bash
pip install pkanban
```

### 2. Initial Configuration
```bash
# For hosted service (recommended)
kanban config --url https://kanban.pearachute.com

# OR for local development
kanban config --url http://localhost:8000
```

### 3. First Login
```bash
kanban login <username> --password <password>
```

## 📋 Core Concepts

**Boards**: Kanban boards containing columns and cards  
**Organizations**: Multi-tenant containers for teams and boards  
**Teams**: Groups within organizations that can share boards  

## 🎯 Essential Commands (Must-Know)

### Basic Board Operations
```bash
# List all boards you can access
kanban boards

# Create a new board
kanban board-create "My Project"

# View board structure
kanban board <board-id>

# Delete a board
kanban board-delete <board-id>
```

### Card Management
```bash
# Create a card
kanban card-create <column-id> "Task title" --description "Details" --position 0

# Update a card (move between columns)
kanban card-update <card-id> "Updated title" --column <new-column-id> --position 0

# Delete a card
kanban card-delete <card-id>
```

### Column Management
```bash
# Create a column
kanban column-create <board-id> "In Progress" 1

# Delete a column
kanban column-delete <column-id>
```

## 🏢 Organization & Team Commands

### Organization Management
```bash
# List organizations
kanban org list

# Create organization
kanban org create "Company Name"

# View organization details
kanban org get <org-id>

# Add member
kanban org member-add <org-id> <username>

# Remove member
kanban org member-remove <org-id> <user-id>
```

### Team Management
```bash
# List teams in organization
kanban team list --org-id <org-id>

# Create team
kanban team create <org-id> "Development Team"

# View team details
kanban team get <team-id>

# Add member to team
kanban team member-add <team-id> <username>
```

### Board Sharing
```bash
# Share board with team
kanban share <board-id> <team-id>

# Make board private
kanban share <board-id> private
```

## 🔧 Configuration & Auth

```bash
# View current config
kanban config

# Change server URL
kanban config --url <new-url>

# Login
kanban login <username> --password <password>

# Logout
kanban logout
```

## 📊 Command Structure

The CLI uses a nested structure:
- **Root commands**: `kanban <command>` (boards, cards, columns)
- **Organization sub-commands**: `kanban org <subcommand>`
- **Team sub-commands**: `kanban team <subcommand>`

## 💡 Pro Tips

1. **Use `kanban boards` first** to see what you can access
2. **Board IDs are numbers** - use them in other commands
3. **Teams exist within organizations** - create org first, then teams
4. **Board sharing is team-based** - share with teams, not individual users
5. **Use `--help`** on any command for options: `kanban board-create --help`

## 🚨 Common Gotchas

- **Must login first** before any board operations
- **Column positions** are 0-based integers
- **Team operations require org-id** as a flag
- **Board sharing replaces existing sharing** (not additive)
- **Card positions** are relative within columns

## 🎭 Typical Agent Workflows

### Setting up a new project:
```bash
kanban board-create "New Project"
kanban board <new-board-id>  # Get default columns
kanban column-create <board-id> "Backlog" 0
kanban column-create <board-id> "In Progress" 1
kanban column-create <board-id> "Done" 2
```

### Setting up team collaboration:
```bash
kanban org create "Project Team"
kanban team create <org-id> "Developers"
kanban org member-add <org-id> <dev-username>
kanban team member-add <team-id> <dev-username>
kanban share <board-id> <team-id>
```

This should get any agent productive with the Kanban CLI within minutes!