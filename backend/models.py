import bcrypt
from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, TextField
from playhouse.sqlite_ext import Model
from datetime import datetime, timezone

from backend.database import db


class BaseModel(Model):
    class Meta:
        database = db


PASSWORD_MAX_LENGTH = 72


class User(BaseModel):
    username = CharField(unique=True, max_length=100)
    password_hash = CharField(max_length=255)

    @classmethod
    def create_user(cls, username, password):
        if len(password) > PASSWORD_MAX_LENGTH:
            raise ValueError(f"Password must be {PASSWORD_MAX_LENGTH} characters or fewer")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return cls.create(username=username, password_hash=password_hash)

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Board(BaseModel):
    user = ForeignKeyField(User, backref="boards")
    name = CharField(max_length=200)
    created_at = DateTimeField()

    @classmethod
    def create_with_columns(cls, user, name, column_names=None):
        if column_names is None:
            column_names = ["To Do", "In Progress", "Done"]

        board = cls.create(user=user, name=name, created_at=datetime.now(timezone.utc))
        for i, col_name in enumerate(column_names):
            Column.create(board=board, name=col_name, position=i)
        return board


class Column(BaseModel):
    board = ForeignKeyField(Board, backref="columns")
    name = CharField(max_length=200)
    position = IntegerField()

    class Meta:
        order_by = ("position",)


class Card(BaseModel):
    column = ForeignKeyField(Column, backref="cards")
    title = CharField(max_length=500)
    description = TextField(null=True)
    position = IntegerField()

    class Meta:
        order_by = ("position",)
