from peewee import CharField, IntegerField, ForeignKeyField, DateTimeField, TextField
from passlib.context import CryptContext
from playhouse.sqlite_ext import Model
from datetime import datetime, timezone

from backend.database import db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True, max_length=100)
    password_hash = CharField(max_length=255)

    @classmethod
    def create_user(cls, username, password):
        password_hash = pwd_context.hash(password)
        return cls.create(username=username, password_hash=password_hash)

    def verify_password(self, password):
        return pwd_context.verify(password, str(self.password_hash))


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
