# kanban board

Board management commands

## Commands

- [`kanban board create`](#kanban-board-create) — Create a new board.
- [`kanban board delete`](#kanban-board-delete) — Delete a board.
- [`kanban board get`](#kanban-board-get) — Show board details with column and card IDs.
- [`kanban board list`](#kanban-board-list) — List all boards.
- [`kanban board update`](#kanban-board-update) — Update board name.

---

## `kanban board create`

Create a new board.

```bash
kanban board create <name>
```

**Arguments**

- `name` (str) — Board name

## `kanban board delete`

Delete a board.

```bash
kanban board delete <board_id>
```

**Arguments**

- `board_id` (int) — Board ID

## `kanban board get`

Show board details with column and card IDs.

```bash
kanban board get <board_id>
```

**Arguments**

- `board_id` (int) — Board ID

## `kanban board list`

List all boards.

```bash
kanban board list
```

## `kanban board update`

Update board name.

```bash
kanban board update <board_id> <name>
```

**Arguments**

- `board_id` (int) — Board ID
- `name` (str) — New board name

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
