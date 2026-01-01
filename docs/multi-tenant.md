# Multi-Tenant Organizations

The application supports multi-tenant organizations with team-based board sharing.

## Organization Model

- **Organizations** group users and teams
- **Organization Members** have roles: `owner`, `admin`, or `member`
- **Teams** are groups of users within an organization
- **Team Members** have roles: `admin` or `member`

## Board Sharing

- Boards are always owned by an individual user
- By default, boards are private (only the owner can access)
- Boards can be shared with a single team for collaboration
- Shared boards: owner + all team members can edit; only owner can delete or change sharing

## Organization API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/organizations` | Create organization (auto-creates "Administrators" team) |
| `GET` | `/api/organizations` | List user's organizations |
| `GET` | `/api/organizations/{id}` | Get organization details |
| `PUT` | `/api/organizations/{id}` | Update organization (owner/admin only) |
| `POST` | `/api/organizations/{id}/members` | Add member |
| `GET` | `/api/organizations/{id}/members` | List members |
| `PUT` | `/api/organizations/{id}/members/{user_id}` | Update member role |
| `DELETE` | `/api/organizations/{id}/members/{user_id}` | Remove member |

## Team API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/organizations/{id}/teams` | Create team |
| `GET` | `/api/organizations/{id}/teams` | List teams |
| `PUT` | `/api/teams/{id}` | Update team (team admin only) |
| `DELETE` | `/api/teams/{id}` | Delete team (org admin only) |
| `POST` | `/api/teams/{id}/members` | Add team member |
| `GET` | `/api/teams/{id}/members` | List team members |
| `PUT` | `/api/teams/{id}/members/{user_id}` | Update team member role |
| `DELETE` | `/api/teams/{id}/members/{user_id}` | Remove team member |

## Board Sharing

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/boards/{id}/share` | Share board with a team (owner only) |

Request body: `{"team_id": null}` to make private, `{"team_id": <team_id>}` to share.
