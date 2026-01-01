import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from backend.auth import Token, create_access_token, get_current_user
from backend.database import db
from backend.models import (
    User, Board, Column, Card, Organization, OrganizationMember,
    Team, TeamMember
)

api = APIRouter()


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def can_access_board(user, board):
    if board.owner == user:
        return True
    if board.shared_team:
        return TeamMember.get_or_none(
            (TeamMember.user == user) &
            (TeamMember.team == board.shared_team)
        ) is not None
    return False


def can_modify_board(user, board):
    return can_access_board(user, board)


def can_delete_board(user, board):
    return board.owner == user


def can_share_board(user, board):
    return board.owner == user


def get_user_organizations(user):
    return Organization.select().join(OrganizationMember).where(OrganizationMember.user == user)


class LoginRequest(BaseModel):
    username: str
    password: str


class BoardCreate(BaseModel):
    name: str


class BoardUpdate(BaseModel):
    name: str


class BoardShare(BaseModel):
    team_id: Optional[int] = None


class BoardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    columns: list
    shared_team_id: Optional[int] = None
    owner_id: int


class ColumnCreate(BaseModel):
    board_id: int
    name: str
    position: int


class ColumnUpdate(BaseModel):
    name: str
    position: int


class ColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: int
    cards: list


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    position: int


class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    created_at: datetime


class OrganizationUpdate(BaseModel):
    name: str


class OrganizationMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime


class OrganizationMemberUpdate(BaseModel):
    role: str


class TeamCreate(BaseModel):
    name: str


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    organization_id: int
    created_at: datetime


class TeamUpdate(BaseModel):
    name: str


class TeamMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    username: str
    role: str
    joined_at: datetime


class TeamMemberUpdate(BaseModel):
    role: str


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
        board = Board.create_with_columns(owner=current_user, name=board_data.name)
    return {"id": board.id}


@api.get("/boards", response_model=list)
async def list_boards(current_user: User = Depends(get_current_user)):
    board_ids = []
    for board in current_user.boards:
        board_ids.append(board.id)
    for tm in current_user.team_memberships:
        for board in tm.team.boards:
            if board.id not in board_ids:
                board_ids.append(board.id)

    boards = Board.select().where(Board.id.in_(board_ids))
    return [
        {
            "id": board.id,
            "name": board.name,
            "created_at": board.created_at,
            "shared_team_id": board.shared_team_id,
            "owner_id": board.owner_id,
        }
        for board in boards
    ]


@api.post("/boards/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    current_user: User = Depends(get_current_user),
):
    board = Board.get_or_none(Board.id == board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not can_modify_board(current_user, board):
        raise HTTPException(status_code=403, detail="Not authorized")
    board.name = board_data.name
    board.save()
    columns = [{"id": c.id, "name": c.name, "position": c.position} for c in board.columns]
    return {
        "id": board.id,
        "name": board.name,
        "created_at": board.created_at,
        "columns": columns,
        "shared_team_id": board.shared_team_id,
        "owner_id": board.owner_id,
    }


@api.get("/boards/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: int, current_user: User = Depends(get_current_user)
):
    board = Board.get_or_none(Board.id == board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not can_access_board(current_user, board):
        raise HTTPException(status_code=403, detail="Not authorized")
    columns = []
    for column in board.columns:
        cards = [{"id": c.id, "title": c.title, "description": c.description, "position": c.position} for c in column.cards]
        columns.append({"id": column.id, "name": column.name, "position": column.position, "cards": cards})
    return {
        "id": board.id,
        "name": board.name,
        "created_at": board.created_at,
        "columns": columns,
        "shared_team_id": board.shared_team_id,
        "owner_id": board.owner_id,
    }


@api.delete("/boards/{board_id}")
async def delete_board(
    board_id: int, current_user: User = Depends(get_current_user)
):
    board = Board.get_or_none(Board.id == board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not can_delete_board(current_user, board):
        raise HTTPException(status_code=403, detail="Only the owner can delete a board")
    with db.atomic():
        for column in board.columns:
            for card in column.cards:
                card.delete_instance()
            column.delete_instance()
        board.delete_instance()
    return {"ok": True}


@api.post("/boards/{board_id}/share")
async def share_board(
    board_id: int,
    share_data: BoardShare,
    current_user: User = Depends(get_current_user),
):
    board = Board.get_or_none(Board.id == board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not can_share_board(current_user, board):
        raise HTTPException(status_code=403, detail="Only the owner can share a board")

    if share_data.team_id is not None:
        team = Team.get_or_none(Team.id == share_data.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        board.shared_team = team
    else:
        board.shared_team = None
    board.save()
    return {"ok": True, "shared_team_id": board.shared_team_id}


@api.post("/columns", response_model=ColumnResponse)
async def create_column(
    column_data: ColumnCreate,
    current_user: User = Depends(get_current_user),
):
    board = Board.get_or_none(Board.id == column_data.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    if not can_modify_board(current_user, board):
        raise HTTPException(status_code=403, detail="Not authorized")
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
    if not can_modify_board(current_user, column.board):
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
    if not can_modify_board(current_user, column.board):
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
    if not can_modify_board(current_user, column.board):
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
    if not can_modify_board(current_user, card.column.board):
        raise HTTPException(status_code=403, detail="Not authorized")
    if card_data.column_id != card.column.id:
        new_column = Column.get_or_none(Column.id == card_data.column_id)
        if not new_column:
            raise HTTPException(status_code=404, detail="New column not found")
        if not can_modify_board(current_user, new_column.board):
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
    if not can_modify_board(current_user, card.column.board):
        raise HTTPException(status_code=403, detail="Not authorized")
    card.delete_instance()
    return {"ok": True}


@api.post("/organizations", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate, current_user: User = Depends(get_current_user)
):
    base_slug = slugify(org_data.name)
    slug = base_slug
    counter = 1
    while Organization.get_or_none(Organization.slug == slug):
        slug = f"{base_slug}-{counter}"
        counter += 1

    with db.atomic():
        org = Organization.create_with_columns(name=org_data.name, slug=slug)
        OrganizationMember.create(
            user=current_user,
            organization=org,
            role="owner",
            joined_at=datetime.now(timezone.utc)
        )
        Team.create_with_columns(name="Administrators", organization=org)

    return {"id": org.id, "name": org.name, "slug": org.slug, "created_at": org.created_at}


@api.get("/organizations", response_model=list)
async def list_organizations(current_user: User = Depends(get_current_user)):
    orgs = get_user_organizations(current_user)
    return [
        {"id": org.id, "name": org.name, "slug": org.slug, "created_at": org.created_at}
        for org in orgs
    ]


@api.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int, current_user: User = Depends(get_current_user)
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return {"id": org.id, "name": org.name, "slug": org.slug, "created_at": org.created_at}


@api.put("/organizations/{org_id}")
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member or member.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update organization")
    org.name = org_data.name
    org.save()
    return {"id": org.id, "name": org.name, "slug": org.slug, "created_at": org.created_at}


@api.post("/organizations/{org_id}/members", response_model=OrganizationMemberResponse)
async def add_organization_member(
    org_id: int,
    request: LoginRequest,
    current_user: User = Depends(get_current_user),
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member or member.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to add members")

    user = User.get_or_none(User.username == request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == user)
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    org_member = OrganizationMember.create(
        user=user,
        organization=org,
        role="member",
        joined_at=datetime.now(timezone.utc)
    )
    return {
        "id": org_member.id,
        "user_id": user.id,
        "username": user.username,
        "role": org_member.role,
        "joined_at": org_member.joined_at,
    }


@api.get("/organizations/{org_id}/members", response_model=list)
async def list_organization_members(
    org_id: int, current_user: User = Depends(get_current_user)
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    members = OrganizationMember.select().where(OrganizationMember.organization == org)
    return [
        {
            "id": m.id,
            "user_id": m.user.id,
            "username": m.user.username,
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m in members
    ]


@api.put("/organizations/{org_id}/members/{user_id}")
async def update_organization_member(
    org_id: int,
    user_id: int,
    update_data: OrganizationMemberUpdate,
    current_user: User = Depends(get_current_user),
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member or member.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    if update_data.role not in ("admin", "member"):
        raise HTTPException(status_code=400, detail="Invalid role")

    target = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user_id == user_id)
    )
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    if target.role == "owner" and update_data.role != "owner":
        raise HTTPException(status_code=400, detail="Cannot demote owner")

    target.role = update_data.role
    target.save()
    return {"ok": True}


@api.delete("/organizations/{org_id}/members/{user_id}")
async def remove_organization_member(
    org_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member")

    target = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user_id == user_id)
    )
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    if target.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove owner")

    is_self = user_id == current_user.id
    is_admin = member.role in ("owner", "admin")

    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    with db.atomic():
        TeamMember.delete().where(TeamMember.user_id == user_id)
        target.delete_instance()

    return {"ok": True}


@api.post("/organizations/{org_id}/teams", response_model=TeamResponse)
async def create_team(
    org_id: int,
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    team = Team.create_with_columns(name=team_data.name, organization=org)
    return {"id": team.id, "name": team.name, "organization_id": org.id, "created_at": team.created_at}


@api.get("/organizations/{org_id}/teams", response_model=list)
async def list_organization_teams(
    org_id: int, current_user: User = Depends(get_current_user)
):
    org = Organization.get_or_none(Organization.id == org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == org) &
        (OrganizationMember.user == current_user)
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    teams = Team.select().where(Team.organization == org)
    return [
        {"id": team.id, "name": team.name, "organization_id": org.id, "created_at": team.created_at}
        for team in teams
    ]


@api.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    tm = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user == current_user)
    )
    if not tm or tm.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update team")

    team.name = team_data.name
    team.save()
    return {"id": team.id, "name": team.name, "organization_id": team.organization_id, "created_at": team.created_at}


@api.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    org_member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == team.organization) &
        (OrganizationMember.user == current_user)
    )
    if not org_member or org_member.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    with db.atomic():
        Board.update(shared_team=None).where(Board.shared_team == team)
        TeamMember.delete().where(TeamMember.team == team)
        team.delete_instance()

    return {"ok": True}


@api.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: int,
    request: LoginRequest,
    current_user: User = Depends(get_current_user),
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    tm = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user == current_user)
    )
    if not tm or tm.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to add members")

    user = User.get_or_none(User.username == request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    org_member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == team.organization) &
        (OrganizationMember.user == user)
    )
    if not org_member:
        raise HTTPException(status_code=400, detail="User is not a member of this organization")

    existing = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user == user)
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already in this team")

    team_member = TeamMember.create(
        user=user,
        team=team,
        role="member",
        joined_at=datetime.now(timezone.utc)
    )
    return {
        "id": team_member.id,
        "user_id": user.id,
        "username": user.username,
        "role": team_member.role,
        "joined_at": team_member.joined_at,
    }


@api.get("/teams/{team_id}/members", response_model=list)
async def list_team_members(
    team_id: int, current_user: User = Depends(get_current_user)
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    org_member = OrganizationMember.get_or_none(
        (OrganizationMember.organization == team.organization) &
        (OrganizationMember.user == current_user)
    )
    if not org_member:
        raise HTTPException(status_code=403, detail="Not a member of this organization")

    members = TeamMember.select().where(TeamMember.team == team)
    return [
        {
            "id": m.id,
            "user_id": m.user.id,
            "username": m.user.username,
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m in members
    ]


@api.put("/teams/{team_id}/members/{user_id}")
async def update_team_member(
    team_id: int,
    user_id: int,
    update_data: TeamMemberUpdate,
    current_user: User = Depends(get_current_user),
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    tm = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user == current_user)
    )
    if not tm or tm.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    if update_data.role not in ("admin", "member"):
        raise HTTPException(status_code=400, detail="Invalid role")

    target = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user_id == user_id)
    )
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    target.role = update_data.role
    target.save()
    return {"ok": True}


@api.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    team = Team.get_or_none(Team.id == team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    tm = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user == current_user)
    )
    if not tm:
        raise HTTPException(status_code=403, detail="Not a team member")

    target = TeamMember.get_or_none(
        (TeamMember.team == team) &
        (TeamMember.user_id == user_id)
    )
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    is_self = user_id == current_user.id
    is_admin = tm.role == "admin"

    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    target.delete_instance()
    return {"ok": True}
