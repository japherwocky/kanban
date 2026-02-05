"""Tests for organization invite system."""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.models import User, Organization, OrganizationMember, OrganizationInvite
from backend.auth import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(
        data={"sub": test_user.id, "username": test_user.username}
    )
    return {"Authorization": f"Bearer {token}"}


import random
import string


def make_unique_slug(base):
    """Generate a unique slug to avoid conflicts."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{base}-{suffix}"


class TestCreateInvite:
    """Tests for POST /api/organizations/{org_id}/invites"""

    def test_owner_can_create_invite(self, client, test_user, db_session):
        """Test that org owner can create an invite."""
        # Create org with unique slug
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "token" in data
        assert data["status"] == "pending"

    def test_owner_can_create_anonymous_invite(self, client, test_user, db_session):
        """Test creating invite without email."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] is None
        assert "token" in data

    def test_non_owner_cannot_create_invite(self, client, test_user, db_session):
        """Test that non-owner cannot create invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        # Create another user
        other_user = User.create_user("otheruser", "password")

        token = create_access_token(
            data={"sub": other_user.id, "username": other_user.username}
        )
        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert "Only the owner can create invites" in response.json()["detail"]

    def test_non_member_cannot_create_invite(self, client, test_user, db_session):
        """Test that non-member cannot create invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        # Create user not in org
        other_user = User.create_user("outsider", "password")

        token = create_access_token(
            data={"sub": other_user.id, "username": other_user.username}
        )
        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        # Non-owners get "Only the owner can create invites" (check runs before member check)
        assert response.status_code == 403

    def test_unauthenticated_cannot_create_invite(self, client, test_user, db_session):
        """Test that unauthenticated requests are rejected."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "test@example.com"},
        )
        assert response.status_code == 401

    def test_organization_not_found(self, client, test_user):
        """Test 404 for non-existent org."""
        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        response = client.post(
            "/api/organizations/99999/invites",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


class TestListInvites:
    """Tests for GET /api/organizations/{org_id}/invites"""

    def test_owner_can_list_invites(self, client, test_user, db_session):
        """Test owner can list invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        # Create an invite first
        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "test@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get(
            f"/api/organizations/{org.id}/invites",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == "test@example.com"

    def test_member_can_list_invites(self, client, test_user, db_session):
        """Test that any org member can list invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        # Add member to org
        member_user = User.create_user("memberuser", "password")
        OrganizationMember.create(
            user=member_user, organization=org, joined_at=datetime.now(timezone.utc)
        )

        # Create an invite (as owner via direct db call)
        invite, _ = OrganizationInvite.create_invite(org, test_user, "test@example.com")

        token = create_access_token(
            data={"sub": member_user.id, "username": member_user.username}
        )
        response = client.get(
            f"/api/organizations/{org.id}/invites",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_non_member_cannot_list_invites(self, client, test_user, db_session):
        """Test that non-members cannot list invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        outsider = User.create_user("outsider2", "password")
        token = create_access_token(
            data={"sub": outsider.id, "username": outsider.username}
        )

        response = client.get(
            f"/api/organizations/{org.id}/invites",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert "Not a member" in response.json()["detail"]


class TestRevokeInvite:
    """Tests for DELETE /api/organizations/{org_id}/invites/{invite_id}"""

    def test_owner_can_revoke_invite(self, client, test_user, db_session):
        """Test that owner can revoke invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        invite, _ = OrganizationInvite.create_invite(org, test_user, "test@example.com")

        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        response = client.delete(
            f"/api/organizations/{org.id}/invites/{invite.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify invite is revoked
        invite_db = OrganizationInvite.get_by_id(invite.id)
        assert invite_db.status == "revoked"

    def test_non_owner_cannot_revoke_invite(self, client, test_user, db_session):
        """Test that non-owner cannot revoke invites."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        member_user = User.create_user("memberrevoke", "password")
        OrganizationMember.create(
            user=member_user, organization=org, joined_at=datetime.now(timezone.utc)
        )

        invite, _ = OrganizationInvite.create_invite(org, test_user, "test@example.com")

        token = create_access_token(
            data={"sub": member_user.id, "username": member_user.username}
        )
        response = client.delete(
            f"/api/organizations/{org.id}/invites/{invite.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert "Only the owner can revoke invites" in response.json()["detail"]

    def test_invite_not_found(self, client, test_user):
        """Test 404 for non-existent invite."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        token = create_access_token(
            data={"sub": test_user.id, "username": test_user.username}
        )
        response = client.delete(
            f"/api/organizations/{org.id}/invites/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404


class TestAcceptInvite:
    """Tests for POST /api/invites/{token}/accept"""

    def test_user_can_accept_invite(self, client, test_user, db_session):
        """Test that user can accept invite and join org."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        new_user = User.create_user("newmember", "password")
        invite, token = OrganizationInvite.create_invite(org, test_user, "new@test.com")

        member_token = create_access_token(
            data={"sub": new_user.id, "username": new_user.username}
        )
        response = client.post(
            f"/api/invites/{token}/accept",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 200
        assert response.json()["ok"] is True

        # Verify user is now a member
        membership = OrganizationMember.get_or_none(
            (OrganizationMember.organization == org)
            & (OrganizationMember.user == new_user)
        )
        assert membership is not None

        # Verify invite is accepted
        invite_db = OrganizationInvite.get_by_id(invite.id)
        assert invite_db.status == "accepted"

    def test_already_member_cannot_accept_invite(self, client, test_user, db_session):
        """Test that existing members cannot accept invite."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        member_user = User.create_user("already_member", "password")
        OrganizationMember.create(
            user=member_user, organization=org, joined_at=datetime.now(timezone.utc)
        )

        invite, token = OrganizationInvite.create_invite(
            org, test_user, "already@test.com"
        )

        member_token = create_access_token(
            data={"sub": member_user.id, "username": member_user.username}
        )
        response = client.post(
            f"/api/invites/{token}/accept",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]

    def test_invalid_token_cannot_be_accepted(self, client, test_user):
        """Test that invalid tokens return 404."""
        new_user = User.create_user("randomuser", "password")
        member_token = create_access_token(
            data={"sub": new_user.id, "username": new_user.username}
        )
        response = client.post(
            "/api/invites/invalid_token_12345/accept",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 404

    def test_revoked_invite_cannot_be_accepted(self, client, test_user, db_session):
        """Test that revoked invites cannot be accepted."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        new_user = User.create_user("newuser2", "password")
        invite, token = OrganizationInvite.create_invite(
            org, test_user, "test@test.com"
        )
        invite.revoke()

        member_token = create_access_token(
            data={"sub": new_user.id, "username": new_user.username}
        )
        response = client.post(
            f"/api/invites/{token}/accept",
            headers={"Authorization": f"Bearer {member_token}"},
        )
        assert response.status_code == 404


class TestGetInvite:
    """Tests for GET /api/invites/{token} (public endpoint)"""

    def test_get_invite_returns_details(self, client, test_user, db_session):
        """Test that get invite returns correct details."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        invite, token = OrganizationInvite.create_invite(
            org, test_user, "test@example.com"
        )

        response = client.get(f"/api/invites/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["organization_name"] == "Test Org"
        assert data["email"] == "test@example.com"
        assert data["status"] == "pending"

    def test_invalid_token_returns_404(self, client):
        """Test that invalid tokens return 404."""
        response = client.get("/api/invites/invalid_token_12345")
        assert response.status_code == 404

    def test_revoked_invite_returns_404(self, client, test_user, db_session):
        """Test that revoked invites return 404."""
        slug = make_unique_slug("test-org")
        org = Organization.create_with_columns("Test Org", slug, test_user)

        invite, token = OrganizationInvite.create_invite(
            org, test_user, "test@test.com"
        )
        invite.revoke()

        response = client.get(f"/api/invites/{token}")
        assert response.status_code == 404
