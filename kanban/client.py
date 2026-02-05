import requests

from kanban.config import get_server_url, get_token, get_api_key


class KanbanClient:
    def __init__(self, server_url=None, token=None, api_key=None):
        self.server_url = server_url or get_server_url()
        self.token = token or get_token()
        self.api_key = api_key or get_api_key()
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})
        elif self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _request(self, method, path, **kwargs):
        url = f"{self.server_url.rstrip('/')}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def login(self, username, password):
        data = self._request(
            "POST", "/api/token", json={"username": username, "password": password}
        )
        return data["access_token"]

    def boards(self):
        return self._request("GET", "/api/boards")

    def board_create(self, name):
        return self._request("POST", "/api/boards", json={"name": name})

    def board_get(self, board_id):
        return self._request("GET", f"/api/boards/{board_id}")

    def board_update(self, board_id, name):
        return self._request("POST", f"/api/boards/{board_id}", json={"name": name})

    def board_delete(self, board_id):
        self._request("DELETE", f"/api/boards/{board_id}")
        return True

    def column_create(self, board_id, name, position):
        return self._request(
            "POST",
            "/api/columns",
            json={"board_id": board_id, "name": name, "position": position},
        )

    def column_update(self, column_id, name, position):
        return self._request(
            "PUT",
            f"/api/columns/{column_id}",
            json={"name": name, "position": position},
        )

    def column_delete(self, column_id):
        self._request("DELETE", f"/api/columns/{column_id}")
        return True

    def card_create(self, column_id, title, description=None, position=0):
        return self._request(
            "POST",
            "/api/cards",
            json={
                "column_id": column_id,
                "title": title,
                "description": description,
                "position": position,
            },
        )

    def card_update(self, card_id, title, description=None, position=0, column_id=None):
        data = {"title": title, "position": position}
        if description is not None:
            data["description"] = description
        if column_id is not None:
            data["column_id"] = column_id
        return self._request("PUT", f"/api/cards/{card_id}", json=data)

    def card_delete(self, card_id):
        self._request("DELETE", f"/api/cards/{card_id}")
        return True

    # Organization methods
    def organizations(self):
        return self._request("GET", "/api/organizations")

    def organization_create(self, name):
        return self._request("POST", "/api/organizations", json={"name": name})

    def organization_get(self, org_id):
        return self._request("GET", f"/api/organizations/{org_id}")

    def organization_update(self, org_id, name):
        return self._request("PUT", f"/api/organizations/{org_id}", json={"name": name})

    def organization_members(self, org_id):
        return self._request("GET", f"/api/organizations/{org_id}/members")

    def organization_member_add(self, org_id, username):
        return self._request(
            "POST", f"/api/organizations/{org_id}/members", json={"username": username}
        )

    def organization_member_update(self, org_id, user_id, role):
        return self._request(
            "PUT", f"/api/organizations/{org_id}/members/{user_id}", json={"role": role}
        )

    def organization_member_remove(self, org_id, user_id):
        self._request("DELETE", f"/api/organizations/{org_id}/members/{user_id}")
        return True

    # Invite methods
    def organization_invite_create(self, org_id, email=None):
        """Create an invite for an organization."""
        data = {}
        if email:
            data["email"] = email
        return self._request("POST", f"/api/organizations/{org_id}/invites", json=data)

    def organization_invites(self, org_id):
        """List pending invites for an organization."""
        return self._request("GET", f"/api/organizations/{org_id}/invites")

    def organization_invite_revoke(self, org_id, invite_id):
        """Revoke an invite."""
        self._request("DELETE", f"/api/organizations/{org_id}/invites/{invite_id}")
        return True

    def invite_get(self, token):
        """Get invite details."""
        return self._request("GET", f"/api/invites/{token}")

    def invite_accept(self, token):
        """Accept an invite."""
        return self._request("POST", f"/api/invites/{token}/accept")

    # Team methods
    def organization_teams(self, org_id):
        return self._request("GET", f"/api/organizations/{org_id}/teams")

    def team_create(self, org_id, name):
        return self._request(
            "POST", f"/api/organizations/{org_id}/teams", json={"name": name}
        )

    def team_get(self, team_id):
        return self._request("GET", f"/api/teams/{team_id}")

    def team_update(self, team_id, name):
        return self._request("PUT", f"/api/teams/{team_id}", json={"name": name})

    def team_delete(self, team_id):
        self._request("DELETE", f"/api/teams/{team_id}")
        return True

    def team_members(self, team_id):
        return self._request("GET", f"/api/teams/{team_id}/members")

    def team_member_add(self, team_id, username):
        return self._request(
            "POST", f"/api/teams/{team_id}/members", json={"username": username}
        )

    def team_member_remove(self, team_id, user_id):
        self._request("DELETE", f"/api/teams/{team_id}/members/{user_id}")
        return True

    # Board sharing
    def board_share(self, board_id, team_id=None):
        data = {"team_id": team_id}
        return self._request("POST", f"/api/boards/{board_id}/share", json=data)

    # API Key methods
    def api_keys(self):
        """List all API keys for the current user."""
        return self._request("GET", "/api/api-keys")

    def api_key_create(self, name, expires_at=None):
        """Create a new API key. Returns the key only once!"""
        data = {"name": name}
        if expires_at:
            data["expires_at"] = expires_at.isoformat()
        return self._request("POST", "/api/api-keys", json=data)

    def api_key_revoke(self, key_id):
        """Deactivate an API key."""
        return self._request("DELETE", f"/api/api-keys/{key_id}")

    def api_key_activate(self, key_id):
        """Reactivate a deactivated API key."""
        return self._request("POST", f"/api/api-keys/{key_id}/activate")
