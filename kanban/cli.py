import sys
from typing import Optional

import typer
from rich import print as rprint

from kanban.config import get_server_url, set_server_url, get_token, set_token, clear_token
from kanban.client import KanbanClient

app = typer.Typer(help="Kanban board CLI", no_args_is_help=True)


def make_client():
    token = get_token()
    if not token:
        rprint("[red]Not logged in. Run 'kanban login' first.[/red]")
        raise typer.Exit(1)
    return KanbanClient()


# === Auth Commands ===

@app.command("config")
def cmd_config(url: Optional[str] = typer.Option(None, "--url", "-u", help="Set the server URL")):
    """Configure the CLI or show current settings."""
    if url:
        set_server_url(url)
        rprint(f"Server URL set to: [green]{url}[/green]")
    else:
        rprint(f"Server URL: [cyan]{get_server_url()}[/cyan]")


@app.command("login")
def cmd_login(
    username: str = typer.Argument(..., help="Username"),
    password: str = typer.Option(..., "--password", "-p", help="Password", hide_input=True),
    server: str = typer.Option("http://localhost:8000", "--server", "-s", help="Server URL"),
):
    """Login to the Kanban server."""
    client = KanbanClient(server_url=server)
    try:
        token = client.login(username, password)
        set_token(token)
        rprint(f"Logged in as [green]{username}[/green]")
    except Exception as e:
        rprint(f"[red]Login failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("logout")
def cmd_logout():
    """Logout and clear credentials."""
    clear_token()
    rprint("Logged out")


# === Board Commands ===

@app.command("boards")
def cmd_boards():
    """List all boards."""
    client = make_client()
    boards = client.boards()
    if not boards:
        rprint("No boards found")
        return
    for b in boards:
        shared_info = ""
        if b.get('shared_team_id'):
            shared_info = f" (shared with team {b['shared_team_id']})"
        elif b.get('is_public_to_org'):
            shared_info = " (public to organization)"
        rprint(f"{b['id']:4}  [bold]{b['name']}[/bold]{shared_info}")


@app.command("board-create")
def cmd_board_create(name: str = typer.Argument(..., help="Board name")):
    """Create a new board."""
    client = make_client()
    result = client.board_create(name)
    rprint(f"Board created with [green]id={result['id']}[/green]")


@app.command("board")
def cmd_board_get(board_id: int = typer.Argument(..., help="Board ID")):
    """Show board details."""
    client = make_client()
    board = client.board_get(board_id)
    rprint(f"Board: [bold]{board['name']}[/bold]")
    for col in board.get("columns", []):
        rprint(f"  [cyan]{col['name']}[/cyan] ({len(col['cards'])} cards)")
        for card in col.get("cards", []):
            rprint(f"    - {card['title']}")


@app.command("board-delete")
def cmd_board_delete(board_id: int = typer.Argument(..., help="Board ID")):
    """Delete a board."""
    client = make_client()
    client.board_delete(board_id)
    rprint("[green]Board deleted[/green]")


# === Column Commands ===

@app.command("column-create")
def cmd_column_create(
    board_id: int = typer.Argument(..., help="Board ID"),
    name: str = typer.Argument(..., help="Column name"),
    position: int = typer.Argument(..., help="Position"),
):
    """Create a new column."""
    client = make_client()
    result = client.column_create(board_id, name, position)
    rprint(f"Column created with [green]id={result['id']}[/green]")


@app.command("column-delete")
def cmd_column_delete(column_id: int = typer.Argument(..., help="Column ID")):
    """Delete a column."""
    client = make_client()
    client.column_delete(column_id)
    rprint("[green]Column deleted[/green]")


# === Card Commands ===

@app.command("card-create")
def cmd_card_create(
    column_id: int = typer.Argument(..., help="Column ID"),
    title: str = typer.Argument(..., help="Card title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Card description"),
    position: int = typer.Option(0, "--position", "-p", help="Position"),
):
    """Create a new card."""
    client = make_client()
    result = client.card_create(column_id, title, description, position)
    rprint(f"Card created with [green]id={result['id']}[/green]")


@app.command("card-update")
def cmd_card_update(
    card_id: int = typer.Argument(..., help="Card ID"),
    title: str = typer.Argument(..., help="Card title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Card description"),
    position: Optional[int] = typer.Option(None, "--position", "-p", help="Position"),
    column: Optional[int] = typer.Option(None, "--column", "-c", help="New column ID"),
):
    """Update a card."""
    client = make_client()
    client.card_update(card_id, title, description, position, column)
    rprint("[green]Card updated[/green]")


@app.command("card-delete")
def cmd_card_delete(card_id: int = typer.Argument(..., help="Card ID")):
    """Delete a card."""
    client = make_client()
    client.card_delete(card_id)
    rprint("[green]Card deleted[/green]")


# === Organization Commands ===

org_app = typer.Typer(help="Organization management commands", no_args_is_help=True)
app.add_typer(org_app, name="org")


@org_app.command("list")
def cmd_organizations():
    """List all organizations."""
    client = make_client()
    orgs = client.organizations()
    if not orgs:
        rprint("No organizations found")
        return
    for org in orgs:
        rprint(f"{org['id']:4}  [bold]{org['name']}[/bold] (owner: {org.get('owner_username', 'Unknown')})")


@org_app.command("create")
def cmd_organization_create(name: str = typer.Argument(..., help="Organization name")):
    """Create a new organization."""
    client = make_client()
    result = client.organization_create(name)
    rprint(f"Organization created with [green]id={result['id']}[/green]")


@org_app.command("get")
def cmd_organization_get(org_id: int = typer.Argument(..., help="Organization ID")):
    """Show organization details."""
    client = make_client()
    org = client.organization_get(org_id)
    rprint(f"Organization: [bold]{org['name']}[/bold]")
    rprint(f"Owner: {org.get('owner_username', 'Unknown')}")
    rprint("Members:")
    for member in org.get("members", []):
        role_info = f" ({member.get('role', 'member')})" if member.get('role') else ""
        rprint(f"  - {member['username']}{role_info}")


@org_app.command("members")
def cmd_organization_members(org_id: int = typer.Argument(..., help="Organization ID")):
    """List organization members."""
    client = make_client()
    members = client.organization_members(org_id)
    for member in members:
        role_info = f" ({member.get('role', 'member')})" if member.get('role') else ""
        rprint(f"{member['id']:4}  {member['username']}{role_info}")


@org_app.command("member-add")
def cmd_organization_member_add(
    org_id: int = typer.Argument(..., help="Organization ID"),
    username: str = typer.Argument(..., help="Username to add"),
):
    """Add member to organization."""
    client = make_client()
    client.organization_member_add(org_id, username)
    rprint(f"Added [green]{username}[/green] to organization")


@org_app.command("member-remove")
def cmd_organization_member_remove(
    org_id: int = typer.Argument(..., help="Organization ID"),
    user_id: int = typer.Argument(..., help="User ID to remove"),
):
    """Remove member from organization."""
    client = make_client()
    client.organization_member_remove(org_id, user_id)
    rprint(f"Removed user [green]{user_id}[/green] from organization")


# === Team Commands ===

team_app = typer.Typer(help="Team management commands", no_args_is_help=True)
app.add_typer(team_app, name="team")


@team_app.command("list")
def cmd_teams(org_id: int = typer.Option(..., "--org-id", "-o", help="Organization ID (required)")):
    """List teams in an organization."""
    client = make_client()
    teams = client.organization_teams(org_id)
    if not teams:
        rprint("No teams found")
        return
    for team in teams:
        rprint(f"{team['id']:4}  [bold]{team['name']}[/bold] (org: {team.get('organization_name', 'Unknown')})")


@team_app.command("create")
def cmd_team_create(
    org_id: int = typer.Argument(..., help="Organization ID"),
    name: str = typer.Argument(..., help="Team name"),
):
    """Create a new team."""
    client = make_client()
    result = client.team_create(org_id, name)
    rprint(f"Team created with [green]id={result['id']}[/green]")


@team_app.command("get")
def cmd_team_get(team_id: int = typer.Argument(..., help="Team ID")):
    """Show team details."""
    client = make_client()
    team = client.team_get(team_id)
    rprint(f"Team: [bold]{team['name']}[/bold]")
    rprint(f"Organization: {team.get('organization_name', 'Unknown')}")
    rprint("Members:")
    for member in team.get("members", []):
        rprint(f"  - {member['username']}")


@team_app.command("members")
def cmd_team_members(team_id: int = typer.Argument(..., help="Team ID")):
    """List team members."""
    client = make_client()
    members = client.team_members(team_id)
    for member in members:
        rprint(f"{member['id']:4}  {member['username']}")


@team_app.command("member-add")
def cmd_team_member_add(
    team_id: int = typer.Argument(..., help="Team ID"),
    username: str = typer.Argument(..., help="Username to add"),
):
    """Add member to team."""
    client = make_client()
    client.team_member_add(team_id, username)
    rprint(f"Added [green]{username}[/green] to team")


@team_app.command("member-remove")
def cmd_team_member_remove(
    team_id: int = typer.Argument(..., help="Team ID"),
    user_id: int = typer.Argument(..., help="User ID to remove"),
):
    """Remove member from team."""
    client = make_client()
    client.team_member_remove(team_id, user_id)
    rprint(f"Removed user [green]{user_id}[/green] from team")


# === Board Sharing ===

@app.command("share")
def cmd_board_share(
    board_id: int = typer.Argument(..., help="Board ID"),
    team_id: str = typer.Argument(..., help="Team ID or 'private' to make board private"),
):
    """Share board with team or make private."""
    client = make_client()
    team_id_value = None if team_id == "private" else team_id
    client.board_share(board_id, team_id_value)
    if team_id_value:
        rprint(f"Board [green]{board_id}[/green] shared with team {team_id_value}")
    else:
        rprint(f"Board [green]{board_id}[/green] made private")


if __name__ == "__main__":
    app()
