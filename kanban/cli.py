import argparse
import sys

from kanban.config import get_server_url, set_server_url, get_token, set_token, clear_token
from kanban.client import KanbanClient


def make_client():
    token = get_token()
    if not token:
        print("Not logged in. Run 'kanban login' first.", file=sys.stderr)
        sys.exit(1)
    return KanbanClient()


def cmd_config(args):
    if args.url:
        set_server_url(args.url)
        print(f"Server URL set to: {args.url}")
    else:
        print(f"Server URL: {get_server_url()}")


def cmd_login(args):
    client = KanbanClient(server_url=args.server)
    try:
        token = client.login(args.username, args.password)
        set_token(token)
        print(f"Logged in as {args.username}")
    except Exception as e:
        print(f"Login failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_logout(args):
    clear_token()
    print("Logged out")


def cmd_boards(args):
    client = make_client()
    boards = client.boards()
    if not boards:
        print("No boards found")
        return
    for b in boards:
        shared_info = ""
        if b.get('shared_team_id'):
            shared_info = f" (shared with team {b['shared_team_id']})"
        elif b.get('is_public_to_org'):
            shared_info = " (public to organization)"
        print(f"{b['id']:4}  {b['name']}{shared_info}")


def cmd_board_create(args):
    client = make_client()
    result = client.board_create(args.name)
    print(f"Board created with id={result['id']}")


def cmd_board_get(args):
    client = make_client()
    board = client.board_get(args.id)
    print(f"Board: {board['name']}")
    for col in board.get("columns", []):
        print(f"  {col['name']} ({len(col['cards'])} cards)")
        for card in col.get("cards", []):
            print(f"    - {card['title']}")


def cmd_board_delete(args):
    client = make_client()
    client.board_delete(args.id)
    print("Board deleted")


def cmd_column_create(args):
    client = make_client()
    result = client.column_create(args.board_id, args.name, args.position)
    print(f"Column created with id={result['id']}")


def cmd_column_delete(args):
    client = make_client()
    client.column_delete(args.id)
    print("Column deleted")


def cmd_card_create(args):
    client = make_client()
    result = client.card_create(args.column_id, args.title, args.description, args.position)
    print(f"Card created with id={result['id']}")


def cmd_card_update(args):
    client = make_client()
    result = client.card_update(args.id, args.title, args.description, args.position, args.column)
    print(f"Card updated")


def cmd_card_delete(args):
    client = make_client()
    client.card_delete(args.id)
    print("Card deleted")


def cmd_organizations(args):
    client = make_client()
    orgs = client.organizations()
    if not orgs:
        print("No organizations found")
        return
    for org in orgs:
        print(f"{org['id']:4}  {org['name']} (owner: {org.get('owner_username', 'Unknown')})")


def cmd_organization_create(args):
    client = make_client()
    result = client.organization_create(args.name)
    print(f"Organization created with id={result['id']}")


def cmd_organization_get(args):
    client = make_client()
    org = client.organization_get(args.id)
    print(f"Organization: {org['name']}")
    print(f"Owner: {org.get('owner_username', 'Unknown')}")
    print("Members:")
    for member in org.get("members", []):
        role_info = f" ({member.get('role', 'member')})" if member.get('role') else ""
        print(f"  - {member['username']}{role_info}")


def cmd_organization_members(args):
    client = make_client()
    members = client.organization_members(args.id)
    for member in members:
        role_info = f" ({member.get('role', 'member')})" if member.get('role') else ""
        print(f"{member['id']:4}  {member['username']}{role_info}")


def cmd_organization_member_add(args):
    client = make_client()
    result = client.organization_member_add(args.org_id, args.username)
    print(f"Added {args.username} to organization")


def cmd_organization_member_remove(args):
    client = make_client()
    client.organization_member_remove(args.org_id, args.user_id)
    print(f"Removed user {args.user_id} from organization")


def cmd_teams(args):
    client = make_client()
    if args.org_id:
        teams = client.organization_teams(args.org_id)
    else:
        print("Organization ID required. Use --org-id to specify.")
        return
    if not teams:
        print("No teams found")
        return
    for team in teams:
        print(f"{team['id']:4}  {team['name']} (org: {team.get('organization_name', 'Unknown')})")


def cmd_team_create(args):
    client = make_client()
    result = client.team_create(args.org_id, args.name)
    print(f"Team created with id={result['id']}")


def cmd_team_get(args):
    client = make_client()
    team = client.team_get(args.id)
    print(f"Team: {team['name']}")
    print(f"Organization: {team.get('organization_name', 'Unknown')}")
    print("Members:")
    for member in team.get("members", []):
        print(f"  - {member['username']}")


def cmd_team_members(args):
    client = make_client()
    members = client.team_members(args.id)
    for member in members:
        print(f"{member['id']:4}  {member['username']}")


def cmd_team_member_add(args):
    client = make_client()
    result = client.team_member_add(args.team_id, args.username)
    print(f"Added {args.username} to team")


def cmd_team_member_remove(args):
    client = make_client()
    client.team_member_remove(args.team_id, args.user_id)
    print(f"Removed user {args.user_id} from team")


def cmd_board_share(args):
    client = make_client()
    team_id = args.team_id if args.team_id != "private" else None
    result = client.board_share(args.board_id, team_id)
    if team_id:
        print(f"Board {args.board_id} shared with team {team_id}")
    else:
        print(f"Board {args.board_id} made private")


def main():
    parser = argparse.ArgumentParser(prog="kanban", description="Kanban board CLI")
    parser.add_argument("--url", help="Override server URL for this command")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    sp_config = subparsers.add_parser("config", help="Configure the CLI")
    sp_config.add_argument("--url", help="Set the server URL")

    sp_login = subparsers.add_parser("login", help="Login to the Kanban server")
    sp_login.add_argument("username", help="Username")
    sp_login.add_argument("password", help="Password")
    sp_login.add_argument("--server", default="http://localhost:8000", help="Server URL")

    subparsers.add_parser("logout", help="Logout and clear credentials")

    sp_boards = subparsers.add_parser("boards", help="List all boards")
    sp_boards.set_defaults(func=cmd_boards)

    sp_board_create = subparsers.add_parser("board-create", help="Create a new board")
    sp_board_create.add_argument("name", help="Board name")
    sp_board_create.set_defaults(func=cmd_board_create)

    sp_board_get = subparsers.add_parser("board", help="Show board details")
    sp_board_get.add_argument("id", type=int, help="Board ID")
    sp_board_get.set_defaults(func=cmd_board_get)

    sp_board_delete = subparsers.add_parser("board-delete", help="Delete a board")
    sp_board_delete.add_argument("id", type=int, help="Board ID")
    sp_board_delete.set_defaults(func=cmd_board_delete)

    sp_column_create = subparsers.add_parser("column-create", help="Create a new column")
    sp_column_create.add_argument("board_id", type=int, help="Board ID")
    sp_column_create.add_argument("name", help="Column name")
    sp_column_create.add_argument("position", type=int, help="Position")
    sp_column_create.set_defaults(func=cmd_column_create)

    sp_column_delete = subparsers.add_parser("column-delete", help="Delete a column")
    sp_column_delete.add_argument("id", type=int, help="Column ID")
    sp_column_delete.set_defaults(func=cmd_column_delete)

    sp_card_create = subparsers.add_parser("card-create", help="Create a new card")
    sp_card_create.add_argument("column_id", type=int, help="Column ID")
    sp_card_create.add_argument("title", help="Card title")
    sp_card_create.add_argument("--description", "-d", default=None, help="Card description")
    sp_card_create.add_argument("--position", "-p", type=int, default=0, help="Position")
    sp_card_create.set_defaults(func=cmd_card_create)

    sp_card_update = subparsers.add_parser("card-update", help="Update a card")
    sp_card_update.add_argument("id", type=int, help="Card ID")
    sp_card_update.add_argument("title", help="Card title")
    sp_card_update.add_argument("--description", "-d", default=None, help="Card description")
    sp_card_update.add_argument("--position", "-p", type=int, default=None, help="Position")
    sp_card_update.add_argument("--column", "-c", type=int, default=None, help="New column ID")
    sp_card_update.set_defaults(func=cmd_card_update)

    sp_card_delete = subparsers.add_parser("card-delete", help="Delete a card")
    sp_card_delete.add_argument("id", type=int, help="Card ID")
    sp_card_delete.set_defaults(func=cmd_card_delete)

    # Organization commands
    sp_organizations = subparsers.add_parser("organizations", help="List organizations")
    sp_organizations.set_defaults(func=cmd_organizations)

    sp_organization_create = subparsers.add_parser("org-create", help="Create an organization")
    sp_organization_create.add_argument("name", help="Organization name")
    sp_organization_create.set_defaults(func=cmd_organization_create)

    sp_organization_get = subparsers.add_parser("org", help="Show organization details")
    sp_organization_get.add_argument("id", type=int, help="Organization ID")
    sp_organization_get.set_defaults(func=cmd_organization_get)

    sp_organization_members = subparsers.add_parser("org-members", help="List organization members")
    sp_organization_members.add_argument("id", type=int, help="Organization ID")
    sp_organization_members.set_defaults(func=cmd_organization_members)

    sp_organization_member_add = subparsers.add_parser("org-member-add", help="Add member to organization")
    sp_organization_member_add.add_argument("org_id", type=int, help="Organization ID")
    sp_organization_member_add.add_argument("username", help="Username to add")
    sp_organization_member_add.set_defaults(func=cmd_organization_member_add)

    sp_organization_member_remove = subparsers.add_parser("org-member-remove", help="Remove member from organization")
    sp_organization_member_remove.add_argument("org_id", type=int, help="Organization ID")
    sp_organization_member_remove.add_argument("user_id", type=int, help="User ID to remove")
    sp_organization_member_remove.set_defaults(func=cmd_organization_member_remove)

    # Team commands
    sp_teams = subparsers.add_parser("teams", help="List teams")
    sp_teams.add_argument("--org-id", type=int, help="Organization ID (required)")
    sp_teams.set_defaults(func=cmd_teams)

    sp_team_create = subparsers.add_parser("team-create", help="Create a team")
    sp_team_create.add_argument("org_id", type=int, help="Organization ID")
    sp_team_create.add_argument("name", help="Team name")
    sp_team_create.set_defaults(func=cmd_team_create)

    sp_team_get = subparsers.add_parser("team", help="Show team details")
    sp_team_get.add_argument("id", type=int, help="Team ID")
    sp_team_get.set_defaults(func=cmd_team_get)

    sp_team_members = subparsers.add_parser("team-members", help="List team members")
    sp_team_members.add_argument("id", type=int, help="Team ID")
    sp_team_members.set_defaults(func=cmd_team_members)

    sp_team_member_add = subparsers.add_parser("team-member-add", help="Add member to team")
    sp_team_member_add.add_argument("team_id", type=int, help="Team ID")
    sp_team_member_add.add_argument("username", help="Username to add")
    sp_team_member_add.set_defaults(func=cmd_team_member_add)

    sp_team_member_remove = subparsers.add_parser("team-member-remove", help="Remove member from team")
    sp_team_member_remove.add_argument("team_id", type=int, help="Team ID")
    sp_team_member_remove.add_argument("user_id", type=int, help="User ID to remove")
    sp_team_member_remove.set_defaults(func=cmd_team_member_remove)

    # Board sharing
    sp_board_share = subparsers.add_parser("board-share", help="Share board with team or make private")
    sp_board_share.add_argument("board_id", type=int, help="Board ID")
    sp_board_share.add_argument("team_id", help="Team ID or 'private' to make board private")
    sp_board_share.set_defaults(func=cmd_board_share)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "config":
        cmd_config(args)
    elif args.command == "login":
        cmd_login(args)
    elif args.command == "logout":
        cmd_logout(args)
    else:
        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
