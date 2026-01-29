import bcrypt  # type: ignore
from peewee import (
    CharField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    TextField,
    BooleanField,
)
from playhouse.sqlite_ext import Model  # type: ignore
from datetime import datetime, timezone

from backend.database import db


class BaseModel(Model):
    class Meta:
        database = db


PASSWORD_MAX_LENGTH = 72


class User(BaseModel):
    username = CharField(unique=True, max_length=100)
    password_hash = CharField(max_length=255)
    email = CharField(max_length=255, null=True)
    admin = BooleanField(default=False)

    @classmethod
    def create_user(cls, username, password, email=None, admin=False):
        if len(password) > PASSWORD_MAX_LENGTH:
            raise ValueError(
                f"Password must be {PASSWORD_MAX_LENGTH} characters or fewer"
            )
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        return cls.create(
            username=username, password_hash=password_hash, email=email, admin=admin
        )

    def verify_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )  # type: ignore


API_KEY_PREFIX = "kanban_"
API_KEY_LENGTH = 32  # Length of the random part (32 chars = 192 bits of entropy)


def generate_api_key():
    """Generate a new API key with the kanban_ prefix."""
    import secrets
    import base64

    random_bytes = base64.urlsafe_b64encode(secrets.token_bytes(24)).decode("utf-8")
    random_bytes = random_bytes.rstrip("=")[:API_KEY_LENGTH]
    return f"{API_KEY_PREFIX}{random_bytes}"


def hash_api_key(key):
    """Hash an API key for storage (like passwords)."""
    return bcrypt.hashpw(key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_api_key_prefix(key):
    """Get the first 8 characters of an API key for identification."""
    return key[:8]


class ApiKey(BaseModel):
    """One-off API keys for agent authentication."""

    user = ForeignKeyField(User, backref="api_keys")
    name = CharField(max_length=100)  # Friendly name (e.g., "CI Agent")
    key_hash = CharField(max_length=255)  # bcrypt hash of the key
    prefix = CharField(max_length=8)  # First 8 chars for identification
    created_at = DateTimeField(default=datetime.now)
    last_used_at = DateTimeField(null=True)
    expires_at = DateTimeField(null=True)  # Optional expiration
    is_active = BooleanField(default=True)

    @classmethod
    def create_key(cls, user, name, expires_at=None):
        """Create a new API key for a user."""
        key = generate_api_key()
        prefix = get_api_key_prefix(key)
        key_hash = hash_api_key(key)
        return cls.create(
            user=user,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            expires_at=expires_at,
        ), key

    def verify(self, key):
        """Verify an API key against the stored hash."""
        return bcrypt.checkpw(key.encode("utf-8"), self.key_hash.encode("utf-8"))

    def deactivate(self):
        """Deactivate this API key."""
        self.is_active = False
        self.save()

    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = datetime.now(timezone.utc)
        self.save()


class Organization(BaseModel):
    name = CharField(max_length=200)
    slug = CharField(max_length=200, unique=True)
    owner = ForeignKeyField(User, backref="owned_organizations")
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, name, slug, owner):
        return cls.create(
            name=name, slug=slug, owner=owner, created_at=datetime.now(timezone.utc)
        )


class OrganizationMember(BaseModel):
    user = ForeignKeyField(User, backref="organization_memberships")
    organization = ForeignKeyField(Organization, backref="members")
    joined_at = DateTimeField()

    class Meta:  # type: ignore
        indexes = ((("user", "organization"), True),)


class Team(BaseModel):
    name = CharField(max_length=200)
    organization = ForeignKeyField(Organization, backref="teams")
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, name, organization):
        return cls.create(
            name=name, organization=organization, created_at=datetime.now(timezone.utc)
        )


class TeamMember(BaseModel):
    user = ForeignKeyField(User, backref="team_memberships")
    team = ForeignKeyField(Team, backref="members")
    joined_at = DateTimeField()

    class Meta:  # type: ignore
        indexes = ((("user", "team"), True),)


class Board(BaseModel):
    owner = ForeignKeyField(User, backref="boards")
    name = CharField(max_length=200)
    shared_team = ForeignKeyField(Team, null=True, backref="boards")
    is_public_to_org = BooleanField(default=False)
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(
        cls, owner, name, shared_team=None, is_public_to_org=False, column_names=None
    ):
        if column_names is None:
            column_names = ["To Do", "In Progress", "For Review"]

        board = cls.create(
            owner=owner,
            name=name,
            shared_team=shared_team,
            is_public_to_org=is_public_to_org,
            created_at=datetime.now(timezone.utc),
        )
        for i, col_name in enumerate(column_names):
            Column.create(board=board, name=col_name, position=i)
        return board


class Column(BaseModel):
    board = ForeignKeyField(Board, backref="columns")
    name = CharField(max_length=200)
    position = IntegerField()


class Card(BaseModel):
    column = ForeignKeyField(Column, backref="cards")
    title = CharField(max_length=500)
    description = TextField(null=True)
    position = IntegerField()


class Comment(BaseModel):
    card = ForeignKeyField(Card, backref="comments")
    user = ForeignKeyField(User, backref="comments")
    content = TextField()
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    @classmethod
    def create_comment(cls, card, user, content):
        return cls.create(
            card=card, user=user, content=content, created_at=datetime.now(timezone.utc)
        )


class BetaSignup(BaseModel):
    email = CharField(max_length=255, unique=True)
    created_at = DateTimeField()
    status = CharField(max_length=50, default="pending")  # pending, invited, rejected

    @classmethod
    def create_signup(cls, email):
        return cls.create(
            email=email, created_at=datetime.now(timezone.utc), status="pending"
        )
