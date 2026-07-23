# kanban team

Team management commands

## Commands

- [`kanban team create`](#kanban-team-create) — Create a new team.
- [`kanban team get`](#kanban-team-get) — Show team details.
- [`kanban team list`](#kanban-team-list) — List teams in an organization.
- [`kanban team member-add`](#kanban-team-member-add) — Add member to team.
- [`kanban team member-remove`](#kanban-team-member-remove) — Remove member from team.
- [`kanban team members`](#kanban-team-members) — List team members.

---

## `kanban team create`

Create a new team.

```bash
kanban team create <org_id> <name>
```

**Arguments**

- `org_id` (int) — Organization ID
- `name` (str) — Team name

## `kanban team get`

Show team details.

```bash
kanban team get <team_id>
```

**Arguments**

- `team_id` (int) — Team ID

## `kanban team list`

List teams in an organization.

```bash
kanban team list --org-id ORG_ID
```

**Options**

- `--org-id`, `-o` (int) _(required)_ — Organization ID (required)

## `kanban team member-add`

Add member to team.

```bash
kanban team member-add <team_id> <username>
```

**Arguments**

- `team_id` (int) — Team ID
- `username` (str) — Username to add

## `kanban team member-remove`

Remove member from team.

```bash
kanban team member-remove <team_id> <user_id>
```

**Arguments**

- `team_id` (int) — Team ID
- `user_id` (int) — User ID to remove

## `kanban team members`

List team members.

```bash
kanban team members <team_id>
```

**Arguments**

- `team_id` (int) — Team ID

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
