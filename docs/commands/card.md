# kanban card

Card management within columns.

## Subcommands

### create

```bash
kanban card create <column_id> <title> [--description <text>] [--position <num>]
```

Create a new card in a column.

**Arguments:**
- `column_id`: Column ID
- `title`: Card title
- `--description`, `-d`: Card description (optional)
- `--position`, `-p`: Position (default: 0)

### update

```bash
kanban card update <card_id> <title> [--description <text>] [--position <num>] [--column <id>]
```

Update a card's title, description, position, or move to another column.

**Arguments:**
- `card_id`: Card ID
- `title`: New card title
- `--description`, `-d`: New description (optional)
- `--position`, `-p`: New position (optional)
- `--column`, `-c`: New column ID (optional)

### delete

```bash
kanban card delete <card_id>
```

Delete a card.

## Example Workflow

```bash
# Create cards
kanban card create 1 "Research competitor analysis" --position 0
kanban card create 1 "Design system architecture" --position 1

# Move cards between columns
kanban card update 2 "Research complete" --column 3 --position 0

# Update card details
kanban card update 2 "Updated title" --description "New description"
```

## See Also

- [Column Commands](/docs/commands/column)
- [CLI Reference](/docs/reference)
