# kanban team

Team management within organizations.

## Subcommands

### list

```bash
kanban team list --org-id <org_id>
```

List teams in an organization.

### create

```bash
kanban team create <org_id> <name>
```

Create a new team within an organization.

### get

```bash
kanban team get <team_id>
```

Show team details and members.

### members

```bash
kanban team members <team_id>
```

List team members.

### member-add

```bash
kanban team member-add <team_id> <username>
```

Add a member to a team.

### member-remove

```bash
kanban team member-remove <team_id> <user_id>
```

Remove a member from a team.

## Example Workflow

```bash
# List teams in your organization
kanban team list --org-id 1

# Create a team
kanban team create 1 "Engineering"

# Get team details
kanban team get 1

# Add members
kanban team member-add 1 alice
kanban team member-add 1 bob
```

## See Also

- [Organization Commands](/docs/commands/org)
- [Board Sharing](/docs/commands/share)
- [CLI Reference](/docs/reference)
