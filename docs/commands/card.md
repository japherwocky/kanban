# kanban card

Card management commands

## Commands

- [`kanban card create`](#kanban-card-create) — Create a new card.
- [`kanban card delete`](#kanban-card-delete) — Delete a card.
- [`kanban card get`](#kanban-card-get) — Show a card's full contents, including its description.
- [`kanban card move`](#kanban-card-move) — Move a card to another column or position, leaving its text alone.
- [`kanban card update`](#kanban-card-update) — Update a card. Anything you don't pass is left unchanged.

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

## `kanban card get`

Show a card's full contents, including its description.

```bash
kanban card get <card_id>
```

**Arguments**

- `card_id` (int) — Card ID

## `kanban card move`

Move a card to another column or position, leaving its text alone.

```bash
kanban card move <card_id> [--column COLUMN] [--position POSITION]
```

**Arguments**

- `card_id` (int) — Card ID

**Options**

- `--column`, `-c` (int) — Destination column ID
- `--position`, `-p` (int) — Position within the column

## `kanban card update`

Update a card. Anything you don't pass is left unchanged.

```bash
kanban card update <card_id> [title] [--description DESCRIPTION] [--position POSITION] [--column COLUMN]
```

**Arguments**

- `card_id` (int) — Card ID
- `title` (str) _(optional)_ — New card title. Omit to leave the title alone.

**Options**

- `--description`, `-d` (str) — Card description
- `--position`, `-p` (int) — Position
- `--column`, `-c` (int) — New column ID

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
