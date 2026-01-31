# kanban share

Share a board with a team or make it private.

## Usage

```bash
kanban share <board_id> <team_id|private>
```

## Arguments

- `board_id`: Board ID
- `team_id`: Team ID to share with (or `private` to make board private)

## Description

Controls who can access a board:
- `private`: Only you can access
- `<team_id>`: All members of that team can access

## Examples

```bash
# Share with a team
kanban share 1 2

# Make board private
kanban share 1 private
```

## See Also

- [Team Commands](/docs/commands/team)
- [CLI Reference](/docs/reference)
