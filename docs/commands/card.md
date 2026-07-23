# kanban card

Card management commands

## Commands

- [`kanban card create`](#kanban-card-create) — Create a new card.
- [`kanban card delete`](#kanban-card-delete) — Delete a card.
- [`kanban card update`](#kanban-card-update) — Update a card.

---

## `kanban card create`

Create a new card.

```bash
kanban card create <column_id> <title> [--description DESCRIPTION] [--position POSITION]
```

**Arguments**

- `column_id` (int) — Column ID
- `title` (str) — Card title

**Options**

- `--description`, `-d` (str) — Card description
- `--position`, `-p` (int) _(default: `0`)_ — Position

## `kanban card delete`

Delete a card.

```bash
kanban card delete <card_id>
```

**Arguments**

- `card_id` (int) — Card ID

## `kanban card update`

Update a card.

```bash
kanban card update <card_id> <title> [--description DESCRIPTION] [--position POSITION] [--column COLUMN]
```

**Arguments**

- `card_id` (int) — Card ID
- `title` (str) — Card title

**Options**

- `--description`, `-d` (str) — Card description
- `--position`, `-p` (int) — Position
- `--column`, `-c` (int) — New column ID

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
