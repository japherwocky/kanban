#!/usr/bin/env python3
"""
Generate markdown documentation pages for each CLI command.

Usage:
    python scripts/generate_cli_docs.py [--output-dir PATH]
"""

from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "commands"

# Command definitions - each entry: (command_name, args, options, description)
COMMANDS = [
    # Root commands
    (
        "config",
        [],
        [("url", "-u", None, "Set the server URL")],
        "Configure the CLI or show current settings.",
    ),
    (
        "login",
        [("username")],
        [
            ("password", "-p", "...", "Password"),
            ("server", "-s", "http://localhost:8000", "Server URL"),
        ],
        "Login to the Kanban server.",
    ),
    ("logout", [], [], "Logout and clear credentials."),
    ("boards", [], [], "List all boards."),
    ("board-create", [("name")], [], "Create a new board."),
    ("board", [("board_id")], [], "Show board details."),
    ("board-delete", [("board_id")], [], "Delete a board."),
    (
        "share",
        [("board_id", "Team ID or 'private' to make board private")],
        [],
        "Share board with team or make private.",
    ),
    # Column commands
    (
        "column create",
        [("board_id", "Board ID"), ("name", "Column name"), ("position", "Position")],
        [],
        "Create a new column.",
    ),
    ("column delete", [("column_id", "Column ID")], [], "Delete a column."),
    # Card commands
    (
        "card create",
        [("column_id", "Column ID"), ("title", "Card title")],
        [
            ("description", "-d", None, "Card description"),
            ("position", "-p", 0, "Position"),
        ],
        "Create a new card.",
    ),
    (
        "card update",
        [("card_id", "Card ID"), ("title", "Card title")],
        [
            ("description", "-d", None, "Card description"),
            ("position", "-p", None, "Position"),
            ("column", "-c", None, "New column ID"),
        ],
        "Update a card.",
    ),
    ("card delete", [("card_id", "Card ID")], [], "Delete a card."),
    # Organization commands
    ("org list", [], [], "List all organizations."),
    ("org create", [("name", "Organization name")], [], "Create a new organization."),
    ("org get", [("org_id", "Organization ID")], [], "Show organization details."),
    ("org members", [("org_id", "Organization ID")], [], "List organization members."),
    (
        "org member-add",
        [("org_id", "Organization ID"), ("username", "Username to add")],
        [],
        "Add member to organization.",
    ),
    (
        "org member-remove",
        [("org_id", "Organization ID"), ("user_id", "User ID to remove")],
        [],
        "Remove member from organization.",
    ),
    # Team commands
    (
        "team list",
        [],
        [("org_id", "-o", "...", "Organization ID (required)")],
        "List teams in an organization.",
    ),
    (
        "team create",
        [("org_id", "Organization ID"), ("name", "Team name")],
        [],
        "Create a new team.",
    ),
    ("team get", [("team_id", "Team ID")], [], "Show team details."),
    ("team members", [("team_id", "Team ID")], [], "List team members."),
    (
        "team member-add",
        [("team_id", "Team ID"), ("username", "Username to add")],
        [],
        "Add member to team.",
    ),
    (
        "team member-remove",
        [("team_id", "Team ID"), ("user_id", "User ID to remove")],
        [],
        "Remove member from team.",
    ),
    # API Key commands
    ("apikey list", [], [], "List all API keys."),
    (
        "apikey create",
        [("name", "Name for the API key (e.g., 'CI Agent')")],
        [],
        "Create a new API key. The key is shown only once - save it securely!",
    ),
    (
        "apikey revoke",
        [("key_id", "API key ID to revoke")],
        [],
        "Revoke (deactivate) an API key.",
    ),
    (
        "apikey activate",
        [("key_id", "API key ID to activate")],
        [],
        "Reactivate a deactivated API key.",
    ),
    (
        "apikey use",
        [
            ("key", "API key to use"),
            ("command", None, "Command to run with this API key"),
        ],
        [],
        "Run a command using an API key instead of login credentials.",
    ),
]


def format_arg(name: str, help_text: str = "") -> str:
    """Format an argument."""
    if help_text:
        return f"- `{name}`: {help_text}"
    return f"- `{name}`"


def format_option(name: str, short: str, default, help_text: str) -> str:
    """Format an option."""
    if default is None:
        opt_str = f"`--{name}` / `-{short}`"
    elif default == "...":
        opt_str = f"`--{name}` / `-{short}` (required)"
    elif isinstance(default, bool):
        if default:
            opt_str = f"`--{name}` / `-{short}` (default: true)"
        else:
            opt_str = f"`--{name}` / `-{short}`"
    elif default is not None:
        opt_str = f"`--{name}` / `-{short}` (default: `{default}`)"
    else:
        opt_str = f"`--{name}` / `-{short}`"

    if help_text:
        opt_str += f": {help_text}"
    return f"- {opt_str}"


def generate_command_page(
    cmd_name: str, args: list, options: list, description: str
) -> str:
    """Generate markdown for a single command."""
    # Build usage line
    parts = cmd_name.split()
    if len(parts) > 1:
        cmd_usage = f"kanban {cmd_name}"
    else:
        cmd_usage = f"kanban {cmd_name}"

    # Add args to usage
    for arg in args:
        arg_name = arg[0]
        cmd_usage += f" <{arg_name}>"

    # Add options to usage
    for opt in options:
        opt_name = opt[0]
        short = opt[1]
        default = opt[2]
        cmd_usage += f" [--{opt_name}|{short} <value>]"

    # Build params section
    lines = ["## Arguments & Options", ""]

    for arg in args:
        lines.append(format_arg(arg[0], arg[1] if len(arg) > 1 else ""))

    for opt in options:
        lines.append(
            format_option(opt[0], opt[1], opt[2], opt[3] if len(opt) > 3 else "")
        )

    return f"""# kanban {cmd_name}

**Command:** `{cmd_usage}`

## Description

{description}

{"## Arguments & Options\n\n" + "\n".join(lines[2:]) if args or options else ""}

## Examples

```bash
{cmd_usage}
```

## See Also

- [CLI Reference](/docs/reference)
"""


def generate_index() -> str:
    """Generate the index page."""
    groups = {
        "Authentication & Configuration": [],
        "Board Management": [],
        "Column Management": [],
        "Card Management": [],
        "Organization Management": [],
        "Team Management": [],
        "API Key Management": [],
    }

    group_map = {
        "config": "Authentication & Configuration",
        "login": "Authentication & Configuration",
        "logout": "Authentication & Configuration",
        "boards": "Board Management",
        "board-create": "Board Management",
        "board": "Board Management",
        "board-delete": "Board Management",
        "share": "Board Management",
        "column": "Column Management",
        "card": "Card Management",
        "org": "Organization Management",
        "team": "Team Management",
        "apikey": "API Key Management",
    }

    for cmd_name, args, options, description in COMMANDS:
        slug = cmd_name.replace(" ", "-")
        first_word = cmd_name.split()[0]
        group = group_map.get(first_word, "Board Management")
        groups[group].append((cmd_name, description))

    lines = [
        "# Kanban CLI Commands",
        "",
        "Complete reference for all Kanban CLI commands.",
        "",
        "## Contents",
        "",
    ]

    for group in groups:
        anchor = group.lower().replace(" & ", "-").replace(" ", "-")
        lines.append(f"- [{group}](#{anchor})")

    lines.extend(["", "---", ""])

    for group, cmds in groups.items():
        if cmds:
            lines.append(f"## {group}")
            lines.append("")
            for cmd_name, description in cmds:
                slug = cmd_name.replace(" ", "-")
                lines.append(f"- [`kanban {cmd_name}`](/docs/{slug})")
                # Take first sentence of description
                first_sentence = (
                    description.split(".")[0] if "." in description else description
                )
                lines.append(f"  - {first_sentence}.")
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Quick Links",
            "",
            "- [Quick Start Guide](/docs/quickstart)",
            "- [Common Workflows](/docs/workflows)",
            "- [Full Reference](/docs/reference)",
        ]
    )

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate CLI docs from command definitions"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=OUTPUT_DIR, help="Output directory"
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating docs to {output_dir}")

    # Generate pages for each command
    for cmd_name, args, options, description in COMMANDS:
        slug = cmd_name.replace(" ", "-")
        content = generate_command_page(cmd_name, args, options, description)
        output_path = output_dir / f"{slug}.md"
        output_path.write_text(content)
        print(f"  Created: {output_path.relative_to(Path(__file__).parent.parent)}")

    # Generate index
    index_content = generate_index()
    index_path = output_dir / "commands.md"
    index_path.write_text(index_content)
    print(f"  Created: {index_path.relative_to(Path(__file__).parent.parent)}")

    print(f"\nGenerated {len(COMMANDS) + 1} markdown files")


if __name__ == "__main__":
    main()
