import requests

from kanban.config import get_server_url, get_token


class KanbanClient:
    def __init__(self, server_url=None, token=None):
        self.server_url = server_url or get_server_url()
        self.token = token or get_token()
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _request(self, method, path, **kwargs):
        url = f"{self.server_url.rstrip('/')}{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def login(self, username, password):
        data = self._request("POST", "/api/token", json={"username": username, "password": password})
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
        return self._request("POST", "/api/columns", json={"board_id": board_id, "name": name, "position": position})

    def column_update(self, column_id, name, position):
        return self._request("PUT", f"/api/columns/{column_id}", json={"name": name, "position": position})

    def column_delete(self, column_id):
        self._request("DELETE", f"/api/columns/{column_id}")
        return True

    def card_create(self, column_id, title, description=None, position=0):
        return self._request("POST", "/api/cards", json={"column_id": column_id, "title": title, "description": description, "position": position})

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
