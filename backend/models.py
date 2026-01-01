import bcrypt  # type: ignore
from peewee import (
    CharField, IntegerField, ForeignKeyField, DateTimeField, TextField,
    BooleanField
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
            raise ValueError(f"Password must be {PASSWORD_MAX_LENGTH} characters or fewer")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls.create(username=username, password_hash=password_hash, email=email, admin=admin)

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))  # type: ignore


class Organization(BaseModel):
    name = CharField(max_length=200)
    slug = CharField(max_length=200, unique=True)
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, name, slug):
        return cls.create(name=name, slug=slug, created_at=datetime.now(timezone.utc))


class OrganizationMember(BaseModel):
    user = ForeignKeyField(User, backref="organization_memberships")
    organization = ForeignKeyField(Organization, backref="members")
    role = CharField(max_length=20)  # owner | admin | member
    joined_at = DateTimeField()

    class Meta:  # type: ignore
        indexes = (
            (("user", "organization"), True),
        )


class Team(BaseModel):
    name = CharField(max_length=200)
    organization = ForeignKeyField(Organization, backref="teams")
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, name, organization):
        return cls.create(name=name, organization=organization, created_at=datetime.now(timezone.utc))


class TeamMember(BaseModel):
    user = ForeignKeyField(User, backref="team_memberships")
    team = ForeignKeyField(Team, backref="members")
    role = CharField(max_length=20)  # admin | member
    joined_at = DateTimeField()

    class Meta:  # type: ignore
        indexes = (
            (("user", "team"), True),
        )


class Board(BaseModel):
    owner = ForeignKeyField(User, backref="boards")
    name = CharField(max_length=200)
    shared_team = ForeignKeyField(Team, null=True, backref="boards")
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, owner, name, shared_team=None, column_names=None):
        if column_names is None:
            column_names = ["To Do", "In Progress", "For Review"]

        board = cls.create(
            owner=owner,
            name=name,
            shared_team=shared_team,
            created_at=datetime.now(timezone.utc)
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
