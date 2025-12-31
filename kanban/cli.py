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
        print(f"{b['id']:4}  {b['name']}")


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
