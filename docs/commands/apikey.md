# kanban apikey

API key management commands

## Commands

- [`kanban apikey activate`](#kanban-apikey-activate) — Reactivate a deactivated API key.
- [`kanban apikey create`](#kanban-apikey-create) — Create a new API key. The key is shown only once - save it securely!
- [`kanban apikey list`](#kanban-apikey-list) — List all API keys.
- [`kanban apikey revoke`](#kanban-apikey-revoke) — Revoke (deactivate) an API key.
- [`kanban apikey save`](#kanban-apikey-save) — Save API key to config file for future use.
- [`kanban apikey use`](#kanban-apikey-use) — Run a command using an API key instead of login credentials.

---

## `kanban apikey activate`

Reactivate a deactivated API key.

```bash
kanban apikey activate <key_id>
```

**Arguments**

- `key_id` (int) — API key ID to activate

## `kanban apikey create`

Create a new API key. The key is shown only once - save it securely!

```bash
kanban apikey create <name>
```

**Arguments**

- `name` (str) — Name for the API key (e.g., 'CI Agent')

## `kanban apikey list`

List all API keys.

```bash
kanban apikey list
```

## `kanban apikey revoke`

Revoke (deactivate) an API key.

```bash
kanban apikey revoke <key_id>
```

**Arguments**

- `key_id` (int) — API key ID to revoke

## `kanban apikey save`

Save API key to config file for future use.

```bash
kanban apikey save <key>
```

**Arguments**

- `key` (str) — API key to save

## `kanban apikey use`

Run a command using an API key instead of login credentials.

```bash
kanban apikey use <key> [command]
```

**Arguments**

- `key` (str) — API key to use
- `command` (str) _(optional)_ — Command to run with this API key

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
