# kanban org

Organization management commands.

## Subcommands

### list

```bash
kanban org list
```

List all organizations you belong to.

### create

```bash
kanban org create <name>
```

Create a new organization. You become the owner.

### get

```bash
kanban org get <org_id>
```

Show organization details including members.

### members

```bash
kanban org members <org_id>
```

List organization members.

### member-add

```bash
kanban org member-add <org_id> <username>
```

Add a member to an organization.

### member-remove

```bash
kanban org member-remove <org_id> <user_id>
```

Remove a member from an organization.

## Example Workflow

```bash
# Create organization
kanban org create "My Company"

# List your organizations
kanban org list

# Get organization details
kanban org get 1

# Add members
kanban org member-add 1 alice
kanban org member-add 1 bob
```

## See Also

- [Team Commands](/docs/commands/team)
- [CLI Reference](/docs/reference)
