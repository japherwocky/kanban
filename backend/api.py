from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.auth import Token, create_access_token, get_current_user
from backend.database import db
from backend.models import User, Board, Column, Card

api = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class BoardCreate(BaseModel):
    name: str


class BoardUpdate(BaseModel):
    name: str


class BoardResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    columns: list

    class Config:
        orm_mode = True


class ColumnCreate(BaseModel):
    board_id: int
    name: str
    position: int


class ColumnUpdate(BaseModel):
    name: str
    position: int


class ColumnResponse(BaseModel):
    id: int
    name: str
    position: int
    cards: list

    class Config:
        orm_mode = True


class CardCreate(BaseModel):
    column_id: int
    title: str
    description: Optional[str] = None
    position: int


class CardUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    position: int
    column_id: int


class CardResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position: int

    class Config:
        orm_mode = True


@api.post("/token", response_model=Token)
async def login(request: LoginRequest):
    user = User.get_or_none(User.username == request.username)
    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@api.post("/boards", response_model=dict)
async def create_board(
    board_data: BoardCreate, current_user: User = Depends(get_current_user)
):
    with db.atomic():
        board = Board.create_with_columns(user=current_user, name=board_data.name)
    return {"id": board.id}


@api.get("/boards", response_model=list)
async def list_boards(current_user: User = Depends(get_current_user)):
    boards = Board.select().where(Board.user == current_user)
    return [
        {
            "id": board.id,
            "name": board.name,
            "created_at": board.created_at,
        }
        for board in boards
    ]


@api.post("/boards/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    current_user: User = Depends(get_current_user),
):
    board = Board.get_or_none(
        (Board.id == board_id) & (Board.user == current_user)
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    board.name = board_data.name
    board.save()
    columns = [{"id": c.id, "name": c.name, "position": c.position} for c in board.columns]
    return {"id": board.id, "name": board.name, "created_at": board.created_at, "columns": columns}


@api.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: int, current_user: User = Depends(get_current_user)
):
    board = Board.get_or_none(
        (Board.id == board_id) & (Board.user == current_user)
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    columns = []
    for column in board.columns:
        cards = [{"id": c.id, "title": c.title, "description": c.description, "position": c.position} for c in column.cards]
        columns.append({"id": column.id, "name": column.name, "position": column.position, "cards": cards})
    return {"id": board.id, "name": board.name, "created_at": board.created_at, "columns": columns}


@api.delete("/boards/{board_id}")
async def delete_board(
    board_id: int, current_user: User = Depends(get_current_user)
):
    board = Board.get_or_none(
        (Board.id == board_id) & (Board.user == current_user)
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    with db.atomic():
        for column in board.columns:
            for card in column.cards:
                card.delete_instance()
            column.delete_instance()
        board.delete_instance()
    return {"ok": True}


@api.post("/columns", response_model=ColumnResponse)
async def create_column(
    column_data: ColumnCreate,
    current_user: User = Depends(get_current_user),
):
    board = Board.get_or_none(
        (Board.id == column_data.board_id) & (Board.user == current_user)
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    column = Column.create(
        board=board,
        name=column_data.name,
        position=column_data.position,
    )
    return {"id": column.id, "name": column.name, "position": column.position, "cards": []}


@api.put("/columns/{column_id}", response_model=ColumnResponse)
async def update_column(
    column_id: int,
    column_data: ColumnUpdate,
    current_user: User = Depends(get_current_user),
):
    column = Column.get_or_none(Column.id == column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    if column.board.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    column.name = column_data.name
    column.position = column_data.position
    column.save()
    cards = [{"id": c.id, "title": c.title, "description": c.description, "position": c.position} for c in column.cards]
    return {"id": column.id, "name": column.name, "position": column.position, "cards": cards}


@api.delete("/columns/{column_id}")
async def delete_column(
    column_id: int, current_user: User = Depends(get_current_user)
):
    column = Column.get_or_none(Column.id == column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    if column.board.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    with db.atomic():
        for card in column.cards:
            card.delete_instance()
        column.delete_instance()
    return {"ok": True}


@api.post("/cards", response_model=CardResponse)
async def create_card(
    card_data: CardCreate,
    current_user: User = Depends(get_current_user),
):
    column = Column.get_or_none(Column.id == card_data.column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    if column.board.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    card = Card.create(
        column=column,
        title=card_data.title,
        description=card_data.description,
        position=card_data.position,
    )
    return {"id": card.id, "title": card.title, "description": card.description, "position": card.position}


@api.put("/cards/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_user),
):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if card.column.board.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if card_data.column_id != card.column.id:
        new_column = Column.get_or_none(Column.id == card_data.column_id)
        if not new_column:
            raise HTTPException(status_code=404, detail="New column not found")
        if new_column.board.user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        card.column = new_column
    card.title = card_data.title
    card.description = card_data.description
    card.position = card_data.position
    card.save()
    return {"id": card.id, "title": card.title, "description": card.description, "position": card.position}


@api.delete("/cards/{card_id}")
async def delete_card(
    card_id: int, current_user: User = Depends(get_current_user)
):
    card = Card.get_or_none(Card.id == card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    if card.column.board.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    card.delete_instance()
    return {"ok": True}
