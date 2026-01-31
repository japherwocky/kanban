# kanban config

Configure the CLI settings.

## Usage

```bash
kanban config [--url <url>]
```

## Options

- `--url`, `-u`: Set the server URL

## Examples

```bash
# Show current configuration
kanban config

# Set server URL
kanban config --url https://kanban.example.com
```

## Configuration File

Settings are stored in `~/.kanban/config.yaml`:

```yaml
server_url: https://kanban.example.com
```

## See Also

- [Login Command](/docs/commands/login)
- [CLI Reference](/docs/reference)
