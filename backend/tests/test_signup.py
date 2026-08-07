"""Tests for self-serve signup and email verification."""

import os
import sys
import random
import string
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.models import (
    User,
    Organization,
    OrganizationMember,
    EmailVerificationToken,
)
from backend.auth import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sent(monkeypatch):
    """Capture outgoing mail instead of sending it.

    Patches send_email, the single choke point every helper in backend.mailer
    funnels through, so the helpers' own link-building still runs and is
    covered here.
    """
    captured = []

    def fake_send_email(to, subject, html):
        captured.append({"to": to, "subject": subject, "html": html})
        return True

    monkeypatch.setattr("backend.mailer.send_email", fake_send_email)
    return captured


def unique(base):
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{base}-{suffix}"


def signup(client, username=None, email=None, password="hunter2hunter2"):
    username = username or unique("newuser").replace("-", "_")
    email = email or f"{unique('someone')}@example.com"
    return client.post(
        "/api/signup",
        json={"username": username, "email": email, "password": password},
    ), username, email


class TestSignup:
    """POST /api/signup"""

    def test_creates_unverified_user_and_sends_one_email(
        self, client, sent, db_session
    ):
        response, username, email = signup(client)

        assert response.status_code == 201
        assert response.json()["email"] == email

        user = User.get_or_none(User.username == username)
        assert user is not None
        assert user.email == email
        assert user.email_verified is False

        assert len(sent) == 1
        assert sent[0]["to"] == email
        # The link the user has to click must actually be in the body.
        token = EmailVerificationToken.get(EmailVerificationToken.user == user).token
        assert f"/verify?token={token}" in sent[0]["html"]

    def test_email_is_normalized_to_lowercase(self, client, sent, db_session):
        response, username, _ = signup(client, email="MiXeD@Example.COM")
        assert response.status_code == 201
        assert User.get(User.username == username).email == "mixed@example.com"

    def test_duplicate_username_rejected(self, client, sent, db_session):
        _, username, _ = signup(client)
        response, _, _ = signup(client, username=username)
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_duplicate_email_rejected(self, client, sent, db_session):
        _, _, email = signup(client)
        response, _, _ = signup(client, email=email)
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_invalid_email_rejected(self, client, sent, db_session):
        response, _, _ = signup(client, email="not-an-email")
        assert response.status_code == 400
        assert sent == []

    def test_overlong_password_rejected(self, client, sent, db_session):
        response, username, _ = signup(client, password="x" * 100)
        assert response.status_code == 400
        assert User.get_or_none(User.username == username) is None

    def test_failed_signup_creates_nothing(self, client, sent, db_session):
        """A rejected signup must not leave a half-made account behind."""
        before = User.select().count()
        signup(client, email="bad")
        assert User.select().count() == before


class TestVerificationGate:
    """Unverified accounts cannot log in."""

    def test_login_refused_until_verified_then_allowed(
        self, client, sent, db_session
    ):
        _, username, _ = signup(client)

        response = client.post(
            "/api/token", json={"username": username, "password": "hunter2hunter2"}
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Email not verified"

        user = User.get(User.username == username)
        token = EmailVerificationToken.get(EmailVerificationToken.user == user).token
        assert client.post("/api/verify-email", json={"token": token}).status_code == 200

        response = client.post(
            "/api/token", json={"username": username, "password": "hunter2hunter2"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_wrong_password_still_401_not_403(self, client, sent, db_session):
        """Verification state must not leak to someone guessing passwords."""
        _, username, _ = signup(client)
        response = client.post(
            "/api/token", json={"username": username, "password": "wrong"}
        )
        assert response.status_code == 401

    def test_admin_created_users_are_verified(self, client, db_session):
        """manage.py and the admin endpoint must not make unusable accounts."""
        user = User.create_user(unique("admin").replace("-", "_"), "password123")
        assert user.email_verified is True


class TestVerifyEmail:
    """POST /api/verify-email"""

    def _token_for(self, client, sent, db_session):
        _, username, _ = signup(client)
        user = User.get(User.username == username)
        return user, EmailVerificationToken.get(EmailVerificationToken.user == user)

    def test_returns_a_working_access_token(self, client, sent, db_session):
        user, record = self._token_for(client, sent, db_session)

        response = client.post("/api/verify-email", json={"token": record.token})
        assert response.status_code == 200

        access_token = response.json()["access_token"]
        me = client.get(
            "/api/boards", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me.status_code == 200

    def test_token_is_single_use(self, client, sent, db_session):
        _, record = self._token_for(client, sent, db_session)

        assert client.post(
            "/api/verify-email", json={"token": record.token}
        ).status_code == 200
        response = client.post("/api/verify-email", json={"token": record.token})
        assert response.status_code == 400
        assert "already been used" in response.json()["detail"]

    def test_expired_token_rejected(self, client, sent, db_session):
        user, record = self._token_for(client, sent, db_session)

        record.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        record.save()

        response = client.post("/api/verify-email", json={"token": record.token})
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()
        assert User.get(User.id == user.id).email_verified is False

    def test_unknown_token_rejected(self, client, db_session):
        response = client.post("/api/verify-email", json={"token": "nope"})
        assert response.status_code == 404


class TestResendVerification:
    """POST /api/resend-verification"""

    def test_cooldown_blocks_a_rapid_second_request(self, client, sent, db_session):
        _, _, email = signup(client)
        response = client.post("/api/resend-verification", json={"email": email})
        assert response.status_code == 429
        assert len(sent) == 1  # only the original signup mail

    def test_sends_once_cooldown_has_passed(self, client, sent, db_session):
        _, username, email = signup(client)
        user = User.get(User.username == username)

        record = EmailVerificationToken.get(EmailVerificationToken.user == user)
        record.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        record.save()

        response = client.post("/api/resend-verification", json={"email": email})
        assert response.status_code == 200
        assert len(sent) == 2

    def test_unknown_email_matches_known_email_response(
        self, client, sent, db_session
    ):
        """No account enumeration: both cases return the same body."""
        _, username, email = signup(client)
        user = User.get(User.username == username)
        record = EmailVerificationToken.get(EmailVerificationToken.user == user)
        record.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
        record.save()

        known = client.post("/api/resend-verification", json={"email": email})
        unknown = client.post(
            "/api/resend-verification", json={"email": "nobody@example.com"}
        )

        assert known.status_code == unknown.status_code == 200
        assert known.json() == unknown.json()

    def test_already_verified_sends_nothing(self, client, sent, db_session):
        _, username, email = signup(client)
        user = User.get(User.username == username)
        user.email_verified = True
        user.save()

        response = client.post("/api/resend-verification", json={"email": email})
        assert response.status_code == 200
        assert len(sent) == 1  # signup mail only


class TestInviteEmail:
    """Org invites are actually delivered now."""

    def test_invite_with_email_is_sent(self, client, sent, test_user, db_session):
        org = Organization.create_with_columns("Acme", unique("acme"), test_user)
        headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user.id, 'username': test_user.username})}"
        }

        response = client.post(
            f"/api/organizations/{org.id}/invites",
            json={"email": "invitee@example.com"},
            headers=headers,
        )
        assert response.status_code == 200

        assert len(sent) == 1
        assert sent[0]["to"] == "invitee@example.com"
        assert f"/invite/{response.json()['token']}" in sent[0]["html"]
        assert "Acme" in sent[0]["html"]

    def test_anonymous_invite_sends_nothing(self, client, sent, test_user, db_session):
        org = Organization.create_with_columns("Acme", unique("acme"), test_user)
        headers = {
            "Authorization": f"Bearer {create_access_token(data={'sub': test_user.id, 'username': test_user.username})}"
        }

        response = client.post(
            f"/api/organizations/{org.id}/invites", json={}, headers=headers
        )
        assert response.status_code == 200
        assert sent == []


class TestSignupGrantsNoOrgAccess:
    """A self-serve account must not land inside anyone else's organization."""

    def _verified_signup(self, client):
        _, username, _ = signup(client)
        user = User.get(User.username == username)
        record = EmailVerificationToken.get(EmailVerificationToken.user == user)
        response = client.post("/api/verify-email", json={"token": record.token})
        return user, {"Authorization": f"Bearer {response.json()['access_token']}"}

    def test_new_account_has_no_organizations(self, client, sent, db_session):
        _, headers = self._verified_signup(client)
        response = client.get("/api/organizations", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_cannot_add_self_to_someone_elses_org(
        self, client, sent, test_user, db_session
    ):
        org = Organization.create_with_columns("Private Co", unique("private"), test_user)
        newcomer, headers = self._verified_signup(client)

        response = client.post(
            f"/api/organizations/{org.id}/members",
            json={"username": newcomer.username},
            headers=headers,
        )
        assert response.status_code == 403
        assert (
            OrganizationMember.get_or_none(
                (OrganizationMember.organization == org)
                & (OrganizationMember.user == newcomer)
            )
            is None
        )
