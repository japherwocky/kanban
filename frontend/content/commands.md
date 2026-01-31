# Kanban CLI Commands

Complete reference for all Kanban CLI commands.

## Contents

- [Authentication & Configuration](#authentication-configuration)
- [Board Management](#board-management)
- [Column Management](#column-management)
- [Card Management](#card-management)
- [Organization Management](#organization-management)
- [Team Management](#team-management)
- [API Key Management](#api-key-management)

---

## Authentication & Configuration

- [`kanban config`](/docs/config)
  - Configure the CLI or show current settings.
- [`kanban login`](/docs/login)
  - Login to the Kanban server.
- [`kanban logout`](/docs/logout)
  - Logout and clear credentials.

## Board Management

- [`kanban boards`](/docs/boards)
  - List all boards.
- [`kanban board-create`](/docs/board-create)
  - Create a new board.
- [`kanban board`](/docs/board)
  - Show board details.
- [`kanban board-delete`](/docs/board-delete)
  - Delete a board.
- [`kanban share`](/docs/share)
  - Share board with team or make private.

## Column Management

- [`kanban column create`](/docs/column-create)
  - Create a new column.
- [`kanban column delete`](/docs/column-delete)
  - Delete a column.

## Card Management

- [`kanban card create`](/docs/card-create)
  - Create a new card.
- [`kanban card update`](/docs/card-update)
  - Update a card.
- [`kanban card delete`](/docs/card-delete)
  - Delete a card.

## Organization Management

- [`kanban org list`](/docs/org-list)
  - List all organizations.
- [`kanban org create`](/docs/org-create)
  - Create a new organization.
- [`kanban org get`](/docs/org-get)
  - Show organization details.
- [`kanban org members`](/docs/org-members)
  - List organization members.
- [`kanban org member-add`](/docs/org-member-add)
  - Add member to organization.
- [`kanban org member-remove`](/docs/org-member-remove)
  - Remove member from organization.

## Team Management

- [`kanban team list`](/docs/team-list)
  - List teams in an organization.
- [`kanban team create`](/docs/team-create)
  - Create a new team.
- [`kanban team get`](/docs/team-get)
  - Show team details.
- [`kanban team members`](/docs/team-members)
  - List team members.
- [`kanban team member-add`](/docs/team-member-add)
  - Add member to team.
- [`kanban team member-remove`](/docs/team-member-remove)
  - Remove member from team.

## API Key Management

- [`kanban apikey list`](/docs/apikey-list)
  - List all API keys.
- [`kanban apikey create`](/docs/apikey-create)
  - Create a new API key.
- [`kanban apikey revoke`](/docs/apikey-revoke)
  - Revoke (deactivate) an API key.
- [`kanban apikey activate`](/docs/apikey-activate)
  - Reactivate a deactivated API key.
- [`kanban apikey use`](/docs/apikey-use)
  - Run a command using an API key instead of login credentials.

---

## Quick Links

- [Quick Start Guide](/docs/quickstart)
- [Common Workflows](/docs/workflows)
- [Full Reference](/docs/reference)