# kanban login

Login to the Kanban server.

```bash
kanban login <username> --password PASSWORD [--server SERVER]
```

**Arguments**

- `username` (str) — Username

**Options**

- `--password`, `-p` (str) _(required)_ — Password. Omit to be prompted (input hidden, stays out of shell history).
- `--server`, `-s` (str) — Server URL. Defaults to the configured URL (see 'kanban config'). Passing it also saves it as the configured URL.

## See Also

- [All Commands](/docs/commands)
- [CLI Reference](/docs/reference)
