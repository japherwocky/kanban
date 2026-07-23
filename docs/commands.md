# Kanban CLI Commands

Complete reference for all Kanban CLI commands.

## Contents

- [Authentication & Configuration](#authentication-configuration)
- [Board Management](#board-management)
- [Column Management](#column-management)
- [Card Management](#card-management)
- [Organization Management](#organization-management)
- [Team Management](#team-management)

---

## Authentication & Configuration

### [`kanban apikey`](/docs/commands/apikey)

API key management commands

- `kanban apikey activate` — Reactivate a deactivated API key.
- `kanban apikey create` — Create a new API key. The key is shown only once - save it securely!
- `kanban apikey list` — List all API keys.
- `kanban apikey revoke` — Revoke (deactivate) an API key.
- `kanban apikey save` — Save API key to config file for future use.
- `kanban apikey use` — Run a command using an API key instead of login credentials.

### [`kanban config`](/docs/commands/config)

Configure the CLI or show current settings.

### [`kanban login`](/docs/commands/login)

Login to the Kanban server.

### [`kanban logout`](/docs/commands/logout)

Logout and clear credentials.

## Board Management

### [`kanban board`](/docs/commands/board)

Board management commands

- `kanban board create` — Create a new board.
- `kanban board delete` — Delete a board.
- `kanban board get` — Show board details with column and card IDs.
- `kanban board list` — List all boards.
- `kanban board update` — Update board name.

### [`kanban share`](/docs/commands/share)

Share board with team or make private.

## Column Management

### [`kanban column`](/docs/commands/column)

Column management commands

- `kanban column create` — Create a new column.
- `kanban column delete` — Delete a column.

## Card Management

### [`kanban card`](/docs/commands/card)

Card management commands

- `kanban card create` — Create a new card.
- `kanban card delete` — Delete a card.
- `kanban card update` — Update a card.

## Organization Management

### [`kanban org`](/docs/commands/org)

Organization management commands

- `kanban org create` — Create a new organization.
- `kanban org get` — Show organization details.
- `kanban org invite-create` — Create an invite link for an organization.
- `kanban org invite-list` — List pending invites for an organization.
- `kanban org invite-revoke` — Revoke a pending invite.
- `kanban org list` — List all organizations.
- `kanban org member-add` — Add member to organization.
- `kanban org member-remove` — Remove member from organization.
- `kanban org members` — List organization members.

## Team Management

### [`kanban team`](/docs/commands/team)

Team management commands

- `kanban team create` — Create a new team.
- `kanban team get` — Show team details.
- `kanban team list` — List teams in an organization.
- `kanban team member-add` — Add member to team.
- `kanban team member-remove` — Remove member from team.
- `kanban team members` — List team members.

---

## Quick Links

- [Quick Start Guide](/docs/quickstart)
- [Common Workflows](/docs/workflows)
- [Full Reference](/docs/reference)
