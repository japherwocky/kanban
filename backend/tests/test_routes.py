"""
Test to verify that FastAPI docs are at /api/docs and /docs is free for frontend
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_docs_route_exists(client):
    """Verify that FastAPI docs are available at /api/docs"""
    response = client.get("/api/docs")
    # Should return HTML for Swagger UI
    assert response.status_code == 200
    assert (
        "swagger" in response.text.lower()
        or "api documentation" in response.text.lower()
    )


def test_api_redoc_route_exists(client):
    """Verify that ReDoc is available at /api/redoc"""
    response = client.get("/api/redoc")
    # Should return HTML for ReDoc
    assert response.status_code == 200
    assert "redoc" in response.text.lower()


def test_api_openapi_json_exists(client):
    """Verify that OpenAPI schema is available at /api/openapi.json"""
    response = client.get("/api/openapi.json")
    # Should return JSON schema
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert "openapi" in data
    assert "paths" in data


def test_docs_route_falls_through_to_spa(client):
    """Verify that /docs falls through to SPA (not handled by FastAPI docs)"""
    response = client.get("/docs")
    # Should fall through to catch-all which returns index.html or API message
    # Importantly, it should NOT be the FastAPI Swagger UI
    assert response.status_code == 200
    # If static files exist, we get HTML; otherwise we get the API message
    # Either way, it's NOT the Swagger UI
    assert "swagger" not in response.text.lower()
    # If we have the built frontend, it should contain the app
    if "<!DOCTYPE html" in response.text or "<html" in response.text:
        # It's serving index.html - good!
        assert True
    else:
        # It's the API message - also fine for testing
        assert (
            "Kanban API is running" in response.text or "docs" in response.text.lower()
        )


def test_api_routes_still_work(client, test_user):
    """Verify that regular API routes still work after the change"""
    from backend.auth import create_access_token

    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Test getting boards
    response = client.get("/api/boards", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
