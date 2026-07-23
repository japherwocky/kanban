# kanban org

Organization management commands

## Commands

- [`kanban org create`](#kanban-org-create) — Create a new organization.
- [`kanban org get`](#kanban-org-get) — Show organization details.
- [`kanban org invite-create`](#kanban-org-invite-create) — Create an invite link for an organization.
- [`kanban org invite-list`](#kanban-org-invite-list) — List pending invites for an organization.
- [`kanban org invite-revoke`](#kanban-org-invite-revoke) — Revoke a pending invite.
- [`kanban org list`](#kanban-org-list) — List all organizations.
- [`kanban org member-add`](#kanban-org-member-add) — Add member to organization.
- [`kanban org member-remove`](#kanban-org-member-remove) — Remove member from organization.
- [`kanban org members`](#kanban-org-members) — List organization members.

---

## `kanban org create`

Create a new organization.

```bash
kanban org create <name>
```

**Arguments**

- `name` (str) — Organization name

## `kanban org get`

Show organization details.

```bash
kanban org get <org_id>
```

**Arguments**

- `org_id` (int) — Organization ID

## `kanban org invite-create`

Create an invite link for an organization.

```bash
kanban org invite-create <org_id> [--email EMAIL]
```

**Arguments**

- `org_id` (int) — Organization ID

**Options**

- `--email`, `-e` (str) — Email of person to invite

## `kanban org invite-list`

List pending invites for an organization.

```bash
kanban org invite-list <org_id>
```

**Arguments**

- `org_id` (int) — Organization ID

## `kanban org invite-revoke`

Revoke a pending invite.

```bash
kanban org invite-revoke <org_id> <invite_id>
```

**Arguments**

- `org_id` (int) — Organization ID
- `invite_id` (int) — Invite ID to revoke

## `kanban org list`

List all organizations.

```bash
kanban org list
```

## `kanban org member-add`

Add member to organization.

```bash
kanban org member-add <org_id> <username>
```

**Arguments**

- `org_id` (int) — Organization ID
- `username` (str) — Username to add

## `kanban org member-remove`

Remove member from organization.

```bash
kanban org member-remove <org_id> <user_id>
```

**Arguments**

- `org_id` (int) — Organization ID
- `user_id` (int) — User ID to remove

## `kanban org members`

List organization members.

```bash
kanban org members <org_id>
```

**Arguments**

- `org_id` (int) — Organization ID

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
