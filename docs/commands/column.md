# kanban column

Column management within boards.

## Subcommands

### create

```bash
kanban column create <board_id> <name> <position>
```

Create a new column in a board.

**Arguments:**
- `board_id`: Board ID
- `name`: Column name
- `position`: 0-based position

### delete

```bash
kanban column delete <column_id>
```

Delete a column and all its cards.

## Example Workflow

```bash
# Create columns in a board
kanban column create 1 "To Do" 0
kanban column create 1 "Doing" 1
kanban column create 1 "Done" 2
```

## See Also

- [Card Commands](/docs/commands/card)
- [Board Commands](/docs/commands/board)
- [CLI Reference](/docs/reference)
