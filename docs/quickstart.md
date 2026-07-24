# Quick Start

Get from `pip install` to a working board in a couple of minutes. Every command
below is copy-pasteable; the ones that print something show the output you
should expect.

This guide covers the day-to-day essentials. For the exhaustive list of
commands and flags, see the [Command Reference](reference) and
[All Commands](commands).

## 1. Install

```bash
pip install pkanban
```

This gives you the `kanban` command. Check it:

```bash
kanban --version
```

## 2. Connect and log in

Point the CLI at a server, then log in. The hosted service is the usual choice:

```bash
kanban config --url https://kanban.pearachute.com
kanban login <your-username> --password <your-password>
```

```
Server URL set to: https://kanban.pearachute.com
Logged in as <your-username>
```

`login` uses whatever URL you configured, so you only set the URL once. Your
token is saved to `~/.kanban.yaml` and reused by every later command — you stay
logged in until you run `kanban logout`.

Self-hosting instead? Point at your own server:

```bash
kanban config --url http://localhost:8000
```

> **Heads up:** the password is passed on the command line, so it lands in your
> shell history. For anything unattended (CI, agents, scripts), use an
> [API key](#4-automating-with-api-keys) instead of a password.

Check your connection and identity any time:

```bash
kanban config          # shows the current server URL
kanban board list      # first thing to confirm you're authenticated
```

## 3. Your first board

A new board starts **empty** — no columns, no cards. You add the columns you
want, then drop cards into them. IDs are printed as you go; you'll pass them to
the next command.

Create a board:

```bash
kanban board create "Roadmap"
```

```
Board created with id=7
```

Add a few columns. The last argument is the position (left to right, 0-based):

```bash
kanban column create 7 "To Do" 0
kanban column create 7 "In Progress" 1
kanban column create 7 "Done" 2
```

```
Column created with id=13
Column created with id=14
Column created with id=15
```

Add a card to the "To Do" column (id `13`):

```bash
kanban card create 13 "Ship v1" --description "Cut the first release" --position 0
```

```
Card created with id=21
```

Now look at the whole board. `board get` is the command you'll reach for most —
it prints every column and card with their IDs:

```bash
kanban board get 7
```

```
Board: Roadmap
  #13 To Do (1 cards)
    - #21 Ship v1
  #14 In Progress (0 cards)
  #15 Done (0 cards)
```

Move the card to "In Progress" (id `14`) by updating its column:

```bash
kanban card update 21 "Ship v1" --column 14
```

That's the full loop: create a board, shape it with columns, and move cards
across it.

## 4. Automating with API keys

For CI, scripts, or agents, authenticate with an API key instead of a password.
Create one while logged in:

```bash
kanban apikey create "CI agent"
```

```
API Key created!

  Name:    CI agent
  Key:     kanban_a1b2c3d4e5f6...
  Prefix:  kanban_a....

IMPORTANT: This key is shown only once! Copy it now and store it securely.
```

Save it once, and every later command uses it — no `kanban login` needed:

```bash
kanban apikey save kanban_a1b2c3d4e5f6...
kanban board list          # now authenticated by the key
```

Manage keys as you'd expect:

```bash
kanban apikey list                 # see keys, when each was last used
kanban apikey revoke <key-id>      # deactivate a key
kanban apikey activate <key-id>    # turn it back on
```

Revoke a key the moment it leaks — that cuts off access without touching your
password or other keys.

## 5. Sharing with a team

Boards are private to you until you share them. Sharing is **team-based**: you
share a board with a team, and everyone on that team gets access. Teams live
inside organizations, so the order is org → team → members → share.

```bash
kanban org create "Acme"                 # prints an org id
kanban team create <org-id> "Engineering" # prints a team id
kanban org member-add <org-id> <username> # add the person to the org
kanban team member-add <team-id> <username> # then to the team
kanban share 7 <team-id>                 # share board 7 with the team
```

Make a board private again at any time:

```bash
kanban share 7 private
```

Inspect what exists:

```bash
kanban org list
kanban org members <org-id>
kanban team list --org-id <org-id>
kanban team members <team-id>
```

Not everyone you want to share with has an account yet? Invite them:

```bash
kanban org invite-create <org-id> --email teammate@example.com
kanban org invite-list <org-id>
```

## How it fits together

```
Organization
  └─ Team ────────────── shared with ──┐
       └─ Members                      │
                                       ▼
User ── owns ──► Board ─► Column ─► Card
```

- **Boards** belong to a user and hold **columns**, which hold **cards**.
- **Organizations** group people; **teams** are subsets of an org.
- **Sharing** connects a board to a team — that's how other people see it.

## Common gotchas

- **New boards have no columns.** Create them yourself (step 3); there's no
  default set.
- **You need to be authenticated first.** Run `kanban login` (or save an API
  key) before any board command, or you'll get an auth error.
- **Positions are 0-based** for both columns and cards, ordered left-to-right
  and top-to-bottom.
- **Sharing replaces, it doesn't stack.** Sharing a board with a new team
  removes the previous team's access rather than adding to it.
- **IDs come from the command that made the thing.** `board get <id>` reprints
  all of them if you lose track.

## Getting help

Every command and subcommand supports `--help`, which lists its exact arguments
and flags:

```bash
kanban --help
kanban board --help
kanban card create --help
```

From here:

- [Command Reference](reference) — every command, grouped and explained
- [Common Workflows](workflows) — recipes for real tasks
- [Authentication](auth) — tokens, API keys, and how sessions work
- [Organizations & Teams](multi-tenant) — the multi-tenant model in depth
