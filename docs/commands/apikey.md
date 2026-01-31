# kanban apikey

API key management for headless and agent access.

## Subcommands

### list

```bash
kanban apikey list
```

List all API keys.

### create

```bash
kanban apikey create <name>
```

Create a new API key. The key is shown only once - save it securely!

### revoke

```bash
kanban apikey revoke <key_id>
```

Revoke (deactivate) an API key.

### activate

```bash
kanban apikey activate <key_id>
```

Reactivate a deactivated API key.

### use

```bash
kanban apikey use <key> <command>
```

Run a command using an API key instead of login credentials.

## Usage with Agents

Agents can use API keys instead of username/password:

```bash
kanban --api-key <key> boards
```

Or inline:

```bash
kanban apikey use <key> boards
```

## See Also

- [CLI Reference](/docs/reference)
- [Authentication](/docs/auth)
