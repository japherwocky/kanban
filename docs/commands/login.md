# kanban login

Login to the Kanban server.

## Usage

```bash
kanban login <username> [--password <password>] [--server <url>]
```

## Arguments

- `username`: Your username

## Options

- `--password`, `-p`: Your password (hidden input)
- `--server`, `-s`: Server URL (default: `http://localhost:8000`)

## Examples

```bash
# Interactive login (prompts for password)
kanban login alice

# With server URL
kanban login alice --server https://kanban.example.com
```

## Authentication

After successful login, credentials are stored in `~/.kanban/config.yaml`.

## See Also

- [Logout Command](/docs/commands/logout)
- [API Key Authentication](/docs/commands/apikey)
- [CLI Reference](/docs/reference)
