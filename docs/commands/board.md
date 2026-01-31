# kanban board

Show board details.

## Usage

```bash
kanban board <board_id>
```

## Arguments

- `board_id`: Board ID

## Description

Displays board name and lists all columns with their cards.

## Output

```
Board: Project Alpha

  To Do (3 cards)
    - Research competitor analysis
    - Design system architecture
    - Set up CI/CD pipeline

  Doing (1 card)
    - Implement user authentication

  Done (5 cards)
    - Project setup
    - Database schema design
    - API design
    - Team onboarding
    - Initial deployment
```

## Examples

```bash
kanban board 1
```

## See Also

- [Boards Command](/docs/commands/boards)
- [Board Create Command](/docs/commands/board-create)
- [Column Commands](/docs/commands/column)
- [CLI Reference](/docs/reference)
