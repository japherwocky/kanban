import os
import secrets
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader


# Secrets that have shipped in this repo as examples. The repo is public, so
# anyone can sign a token with one and become any user. Refusing to start beats
# running on a key an attacker can read off GitHub.
PLACEHOLDER_SECRETS = frozenset(
    {
        "change-this-in-production",
        "your-super-secret-jwt-key-here-change-this-in-production",
    }
)


def _secret_file_path() -> str:
    """Where a generated secret lives: beside the database, the other piece of
    per-deployment state the service already owns and can write to."""
    override = os.environ.get("JWT_SECRET_FILE")
    if override:
        return override

    database_path = os.environ.get("DATABASE_PATH", "")
    if database_path and not database_path.startswith("file:"):
        directory = os.path.dirname(os.path.abspath(database_path))
    else:
        # No database file to sit next to (unset, or an in-memory URI).
        directory = os.getcwd()
    return os.path.join(directory, ".jwt_secret")


def _read_secret_file(path: str) -> str:
    try:
        with open(path) as handle:
            return handle.read().strip()
    except FileNotFoundError:
        return ""


def _read_or_create_secret(path: str) -> str:
    existing = _read_secret_file(path)
    if existing:
        return existing

    generated = secrets.token_urlsafe(48)
    try:
        # O_EXCL so two workers starting at once cannot install competing
        # secrets -- whoever loses the race reads the winner's file instead,
        # and every process ends up signing with the same key.
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return _read_secret_file(path) or generated
    except OSError as exc:
        raise RuntimeError(
            f"Could not write a JWT signing key to {path}: {exc}\n"
            "Set JWT_SECRET_KEY in the environment, or point JWT_SECRET_FILE at "
            "a writable path.\n"
            "Generate one with: "
            'python -c "import secrets; print(secrets.token_urlsafe(48))"'
        ) from exc

    with os.fdopen(descriptor, "w") as handle:
        handle.write(generated)

    print(
        f"kanban: no JWT_SECRET_KEY set, generated a signing key at {path}.\n"
        "kanban: existing sessions are now invalid; users will need to log in "
        "again.\n"
        "kanban: set JWT_SECRET_KEY explicitly to manage the key yourself.",
        file=sys.stderr,
    )
    return generated


def _load_secret_key() -> str:
    """Resolve the JWT signing key, refusing to fall back to a public constant.

    An explicit JWT_SECRET_KEY always wins. Unset, we generate a real key and
    persist it rather than failing to boot -- a self-hosted install that never
    configured one should end up secure, not down.
    """
    configured = os.environ.get("JWT_SECRET_KEY", "").strip()
    if configured in PLACEHOLDER_SECRETS:
        raise RuntimeError(
            "JWT_SECRET_KEY is still set to the example value from this "
            "repository, which is public -- anyone could forge a login token "
            "for any account.\n"
            "Replace it with a real secret: "
            'python -c "import secrets; print(secrets.token_urlsafe(48))"\n'
            "Or unset JWT_SECRET_KEY entirely and one will be generated for you."
        )
    if configured:
        return configured

    return _read_or_create_secret(_secret_file_path())


SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id_str = payload.get("sub", "0")
    user_id = int(user_id_str) if user_id_str else 0
    username: str = str(payload.get("username", ""))
    if user_id == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenData(user_id=user_id, username=username)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    token = credentials.credentials
    token_data = decode_token(token)

    from backend.models import User

    user = User.get_or_none(User.id == token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    token = credentials.credentials
    token_data = decode_token(token)

    from backend.models import User

    user = User.get_or_none(User.id == token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_current_user_from_api_key_header(api_key: str):
    """Validate an API key from the header value."""
    from backend.models import ApiKey
    from datetime import timezone as tz

    # Look up API key by prefix (first 8 chars)
    prefix = api_key[:8]
    api_key_record = ApiKey.get_or_none(ApiKey.prefix == prefix)

    if api_key_record is None:
        return None

    if not api_key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive",
        )

    # Check expiration
    if api_key_record.expires_at and api_key_record.expires_at.replace(
        tzinfo=tz.utc
    ) < datetime.now(tz.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
        )

    # Verify the key
    if not api_key_record.verify(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Update last used timestamp
    api_key_record.update_last_used()

    return api_key_record.user


async def get_current_user_or_api_key(
    request: Request,
):
    """
    Try to authenticate via API key first, then fall back to JWT.
    Either authentication method returns the authenticated user.
    """
    # Check for API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        user_from_api_key = await get_current_user_from_api_key_header(api_key)
        if user_from_api_key is not None:
            return user_from_api_key

    # Fall back to JWT Bearer token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            token_data = decode_token(token)
            from backend.models import User

            user = User.get_or_none(User.id == token_data.user_id)
            if user is not None:
                return user
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
