"""Sliding session expiration.

ACCESS_TOKEN_EXPIRE_MINUTES is absolute from the moment a token is minted, and
nothing used to re-issue it -- so a user logged out exactly 24h after logging
in no matter how continuously they had been using the app. The server now hands
back a replacement token on a header once the current one is close to expiry.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import (  # noqa: E402
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    RENEWED_TOKEN_HEADER,
    SECRET_KEY,
    SESSION_ABSOLUTE_MAX_DAYS,
    TOKEN_RENEWAL_WINDOW_MINUTES,
    create_access_token,
    renew_access_token,
)
from backend.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


def claims(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def token_for(user, *, age_minutes=0, auth_time=None):
    """A token as it would look `age_minutes` after being minted."""
    remaining = ACCESS_TOKEN_EXPIRE_MINUTES - age_minutes
    data = {"sub": user.id, "username": user.username}
    if auth_time is not None:
        data["auth_time"] = auth_time
    return create_access_token(data=data, expires_delta=timedelta(minutes=remaining))


def now():
    return datetime.now(timezone.utc).timestamp()


class TestRenewalDecision:
    def test_fresh_token_is_left_alone(self, test_user):
        assert renew_access_token(token_for(test_user)) is None

    def test_token_inside_the_renewal_window_is_replaced(self, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - TOKEN_RENEWAL_WINDOW_MINUTES + 1
        renewed = renew_access_token(token_for(test_user, age_minutes=aged))

        assert renewed is not None
        assert claims(renewed)["sub"] == str(test_user.id)
        assert claims(renewed)["username"] == test_user.username

    def test_renewal_extends_the_expiry(self, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        old = token_for(test_user, age_minutes=aged)
        renewed = renew_access_token(old)

        assert claims(renewed)["exp"] > claims(old)["exp"]
        assert claims(renewed)["exp"] > now() + (ACCESS_TOKEN_EXPIRE_MINUTES - 1) * 60

    def test_garbage_is_not_renewed(self, test_user):
        assert renew_access_token("not-a-jwt") is None
        assert renew_access_token("") is None

    def test_token_signed_with_another_key_is_not_renewed(self, test_user):
        forged = jwt.encode(
            {"sub": str(test_user.id), "exp": now() + 60},
            "some-other-key",
            algorithm=ALGORITHM,
        )
        assert renew_access_token(forged) is None


class TestAbsoluteCap:
    """Renewal cannot go on forever: these JWTs are stateless and cannot be
    revoked, so an unbounded slide would keep a stolen token alive for good."""

    def test_auth_time_survives_renewal(self, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        original_auth_time = int(now() - 5 * 24 * 60 * 60)
        renewed = renew_access_token(
            token_for(test_user, age_minutes=aged, auth_time=original_auth_time)
        )

        # Carried forward, not reset -- otherwise each renewal would restart
        # the clock and the cap below could never be reached.
        assert claims(renewed)["auth_time"] == original_auth_time

    def test_renewal_stops_past_the_absolute_maximum(self, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        long_ago = int(now() - (SESSION_ABSOLUTE_MAX_DAYS + 1) * 24 * 60 * 60)

        assert (
            renew_access_token(
                token_for(test_user, age_minutes=aged, auth_time=long_ago)
            )
            is None
        )

    def test_renewal_still_works_just_inside_the_maximum(self, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        just_inside = int(now() - (SESSION_ABSOLUTE_MAX_DAYS - 1) * 24 * 60 * 60)

        assert (
            renew_access_token(
                token_for(test_user, age_minutes=aged, auth_time=just_inside)
            )
            is not None
        )

    def test_token_predating_auth_time_derives_one_from_its_expiry(self, test_user):
        """Sessions live at deploy time have no auth_time claim. Refusing them
        renewal would cut every one of them off at its next cliff -- the exact
        failure this change exists to remove."""
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        legacy = jwt.encode(
            {
                "sub": str(test_user.id),
                "username": test_user.username,
                "exp": now() + (ACCESS_TOKEN_EXPIRE_MINUTES - aged) * 60,
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        assert "auth_time" not in claims(legacy)

        renewed = renew_access_token(legacy)
        assert renewed is not None
        # Derived as "issued one full window before it expires", so the cap is
        # measured from something real rather than from now.
        assert claims(renewed)["auth_time"] < now()


class TestRenewalOverHttp:
    def test_aging_token_comes_back_renewed(self, client, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        old = token_for(test_user, age_minutes=aged)

        response = client.get("/api/boards", headers={"Authorization": f"Bearer {old}"})

        assert response.status_code == 200
        renewed = response.headers.get(RENEWED_TOKEN_HEADER)
        assert renewed and renewed != old
        assert claims(renewed)["sub"] == str(test_user.id)

    def test_the_renewed_token_actually_works(self, client, test_user):
        aged = ACCESS_TOKEN_EXPIRE_MINUTES - 1
        old = token_for(test_user, age_minutes=aged)

        first = client.get("/api/boards", headers={"Authorization": f"Bearer {old}"})
        renewed = first.headers[RENEWED_TOKEN_HEADER]

        second = client.get(
            "/api/boards", headers={"Authorization": f"Bearer {renewed}"}
        )
        assert second.status_code == 200
        # And the fresh one is not itself immediately renewed again.
        assert RENEWED_TOKEN_HEADER not in second.headers

    def test_fresh_token_gets_no_header(self, client, test_user):
        response = client.get(
            "/api/boards",
            headers={"Authorization": f"Bearer {token_for(test_user)}"},
        )

        assert response.status_code == 200
        assert RENEWED_TOKEN_HEADER not in response.headers

    def test_unauthenticated_request_gets_no_header(self, client):
        response = client.get("/api/health")

        assert RENEWED_TOKEN_HEADER not in response.headers

    def test_api_key_auth_is_untouched(self, client, test_user):
        """API keys do not expire, arrive on their own header, and have nothing
        to renew -- agents are on this path and must not be handed a JWT."""
        from backend.models import ApiKey

        _, raw_key = ApiKey.create_key(test_user, "renewal test")
        response = client.get("/api/boards", headers={"X-API-Key": raw_key})

        assert response.status_code == 200
        assert RENEWED_TOKEN_HEADER not in response.headers


class TestLoginStampsAuthTime:
    def test_login_token_carries_auth_time(self, client, test_user):
        response = client.post(
            "/api/token",
            json={"username": test_user.username, "password": "testpassword"},
        )

        assert response.status_code == 200
        auth_time = claims(response.json()["access_token"])["auth_time"]
        assert abs(auth_time - now()) < 60
