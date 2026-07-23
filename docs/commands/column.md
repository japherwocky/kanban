# kanban column

Column management commands

## Commands

- [`kanban column create`](#kanban-column-create) — Create a new column.
- [`kanban column delete`](#kanban-column-delete) — Delete a column.

---

## `kanban column create`

Create a new column.

```bash
kanban column create <board_id> <name> <position>
```

**Arguments**

- `board_id` (int) — Board ID
- `name` (str) — Column name
- `position` (int) — Position

## `kanban column delete`

Delete a column.

```bash
kanban column delete <column_id>
```

**Arguments**

- `column_id` (int) — Column ID

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
