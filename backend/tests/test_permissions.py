import os
import sys
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone

os.environ["DATABASE_PATH"] = "test_kanban.db"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database import db
from backend.models import User, Board, Column, Card, Organization, OrganizationMember, Team, TeamMember
from backend.auth import create_access_token


@pytest.fixture
def test_db():
    db.connect()
    # Drop and recreate tables to ensure clean state
    db.drop_tables([Card, Column, Board, TeamMember, Team, OrganizationMember, Organization, User])
    db.create_tables([User, Board, Column, Card, Organization, OrganizationMember, Team, TeamMember])
    yield db
    # Cleanup after each test
    for table in [Card, Column, Board, TeamMember, Team, OrganizationMember, Organization, User]:
        try:
            table.delete().execute()
        except:
            pass
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


def create_user(username, password):
    return User.create_user(username, password)


def get_auth_headers(user):
    token = create_access_token(data={"sub": user.id, "username": user.username})
    return {"Authorization": f"Bearer {token}"}


# ===============================
# ORGANIZATION PERMISSION TESTS
# ===============================

def test_create_organization_requires_auth(client):
    """Creating an organization requires authentication"""
    response = client.post("/api/organizations", json={"name": "Test Org"})
    assert response.status_code == 403


def test_any_user_can_create_organization(client, test_db):
    """Any authenticated user can create an organization"""
    user = create_user("orguser1", "password")
    headers = get_auth_headers(user)

    response = client.post("/api/organizations", json={"name": "My Org"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Org"
    assert "id" in data


def test_list_organizations_returns_only_user_orgs(client, test_db):
    """List organizations should only return orgs user is a member of"""
    user1 = create_user("orguser1", "password")
    user2 = create_user("orguser2", "password")

    # Create org as user1
    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user1, organization=org, role="owner", joined_at=datetime.now(timezone.utc))

    # Create another org as user2
    org2 = Organization.create(name="Org2", slug="org2", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user2, organization=org2, role="owner", joined_at=datetime.now(timezone.utc))

    # user1 should only see their org
    headers1 = get_auth_headers(user1)
    response = client.get("/api/organizations", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == org.id


def test_get_organization_requires_membership(client, test_db):
    """Getting an org requires being a member"""
    user1 = create_user("orguser1", "password")
    user2 = create_user("orguser2", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user1, organization=org, role="owner", joined_at=datetime.now(timezone.utc))

    # user2 cannot access
    headers2 = get_auth_headers(user2)
    response = client.get(f"/api/organizations/{org.id}", headers=headers2)
    assert response.status_code == 403


def test_update_organization_requires_owner_or_admin(client, test_db):
    """Updating organization requires owner or admin role"""
    owner = create_user("owner", "password")
    admin = create_user("admin", "password")
    member = create_user("member", "password")

    org = Organization.create(name="Original Name", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # Owner can update
    response = client.put(
        f"/api/organizations/{org.id}",
        json={"name": "Updated by Owner"},
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Admin can update
    response = client.put(
        f"/api/organizations/{org.id}",
        json={"name": "Updated by Admin"},
        headers=get_auth_headers(admin)
    )
    assert response.status_code == 200

    # Member cannot update
    response = client.put(
        f"/api/organizations/{org.id}",
        json={"name": "Should Not Update"},
        headers=get_auth_headers(member)
    )
    assert response.status_code == 403


# ===============================
# ORGANIZATION MEMBER PERMISSION TESTS
# ===============================

def test_add_org_member_requires_owner_or_admin(client, test_db):
    """Adding organization members requires owner or admin role"""
    owner = create_user("owner", "password")
    member = create_user("member", "password")
    new_user = create_user("newuser", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # Owner can add
    response = client.post(
        f"/api/organizations/{org.id}/members",
        json={"username": "newuser"},
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Member cannot add
    response = client.post(
        f"/api/organizations/{org.id}/members",
        json={"username": "member"},  # Already in org, but should fail on permission
        headers=get_auth_headers(member)
    )
    assert response.status_code == 403


def test_update_org_member_role_requires_owner_or_admin(client, test_db):
    """Updating member role requires owner or admin role"""
    owner = create_user("owner", "password")
    admin = create_user("admin", "password")
    member = create_user("member", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # Owner can update
    response = client.put(
        f"/api/organizations/{org.id}/members/{member.id}",
        json={"role": "admin"},
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Admin can update
    response = client.put(
        f"/api/organizations/{org.id}/members/{member.id}",
        json={"role": "member"},
        headers=get_auth_headers(admin)
    )
    assert response.status_code == 200

    # Member cannot update
    response = client.put(
        f"/api/organizations/{org.id}/members/{admin.id}",
        json={"role": "member"},
        headers=get_auth_headers(member)
    )
    assert response.status_code == 403


def test_cannot_demote_org_owner(client, test_db):
    """Cannot demote an organization owner"""
    owner = create_user("owner", "password")
    admin = create_user("admin", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))

    # Admin cannot demote owner
    response = client.put(
        f"/api/organizations/{org.id}/members/{owner.id}",
        json={"role": "admin"},
        headers=get_auth_headers(admin)
    )
    assert response.status_code == 400


def test_remove_org_member_permissions(client, test_db):
    """Removing org member: admin/owner can remove others, anyone can remove self"""
    owner = create_user("owner", "password")
    admin = create_user("admin", "password")
    member = create_user("member", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # Owner can remove member
    response = client.delete(
        f"/api/organizations/{org.id}/members/{member.id}",
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Recreate member for next test
    member = OrganizationMember.create(user=member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # Admin can remove member
    response = client.delete(
        f"/api/organizations/{org.id}/members/{member.id}",
        headers=get_auth_headers(admin)
    )
    assert response.status_code == 200

    # Member cannot remove another member
    member2 = create_user("member2", "password")
    org_member = OrganizationMember.create(user=member2, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    response = client.delete(
        f"/api/organizations/{org.id}/members/{org_member.id}",
        headers=get_auth_headers(member)
    )
    assert response.status_code == 403


def test_cannot_remove_org_owner(client, test_db):
    """Cannot remove an organization owner"""
    owner = create_user("owner", "password")
    admin = create_user("admin", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    owner_member = OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))

    # Admin cannot remove owner
    response = client.delete(
        f"/api/organizations/{org.id}/members/{owner.id}",
        headers=get_auth_headers(admin)
    )
    assert response.status_code == 400


# ===============================
# TEAM PERMISSION TESTS
# ===============================

def test_create_team_requires_org_membership(client, test_db):
    """Creating a team requires being an org member"""
    user1 = create_user("user1", "password")
    user2 = create_user("user2", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user1, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    # user1 (org member) can create team
    response = client.post(
        f"/api/organizations/{org.id}/teams",
        json={"name": "New Team"},
        headers=get_auth_headers(user1)
    )
    assert response.status_code == 200

    # user2 (not org member) cannot create team
    response = client.post(
        f"/api/organizations/{org.id}/teams",
        json={"name": "Should Not Create"},
        headers=get_auth_headers(user2)
    )
    assert response.status_code == 403


def test_list_teams_requires_org_membership(client, test_db):
    """Listing teams requires being an org member"""
    user1 = create_user("user1", "password")
    user2 = create_user("user2", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user1, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))

    # user1 (org member) can list teams
    response = client.get(f"/api/organizations/{org.id}/teams", headers=get_auth_headers(user1))
    assert response.status_code == 200
    assert len(response.json()) == 1

    # user2 (not org member) cannot list teams
    response = client.get(f"/api/organizations/{org.id}/teams", headers=get_auth_headers(user2))
    assert response.status_code == 403


def test_update_team_requires_team_admin(client, test_db):
    """Updating a team requires being a team admin"""
    team_admin = create_user("teamadmin", "password")
    team_member = create_user("teammember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # Team admin can update
    response = client.put(
        f"/api/teams/{team.id}",
        json={"name": "Updated Name"},
        headers=get_auth_headers(team_admin)
    )
    assert response.status_code == 200

    # Team member cannot update
    response = client.put(
        f"/api/teams/{team.id}",
        json={"name": "Should Not Update"},
        headers=get_auth_headers(team_member)
    )
    assert response.status_code == 403


def test_delete_team_requires_org_owner_or_admin(client, test_db):
    """Deleting a team requires org owner or admin"""
    org_owner = create_user("owner", "password")
    org_admin = create_user("orgadmin", "password")
    team_admin = create_user("teamadmin", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=org_owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=org_admin, organization=org, role="admin", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))

    # Org owner can delete team
    team2 = Team.create(name="Team2", organization=org, created_at=datetime.now(timezone.utc))
    response = client.delete(f"/api/teams/{team2.id}", headers=get_auth_headers(org_owner))
    assert response.status_code == 200

    # Org admin can delete team
    response = client.delete(f"/api/teams/{team.id}", headers=get_auth_headers(org_admin))
    assert response.status_code == 200

    # Team admin cannot delete team (unless also org admin/owner)
    team3 = Team.create(name="Team3", organization=org, created_at=datetime.now(timezone.utc))
    response = client.delete(f"/api/teams/{team3.id}", headers=get_auth_headers(team_admin))
    assert response.status_code == 403


# ===============================
# TEAM MEMBER PERMISSION TESTS
# ===============================

def test_add_team_member_requires_team_admin(client, test_db):
    """Adding team member requires being a team admin"""
    team_admin = create_user("teamadmin", "password")
    team_member = create_user("teammember", "password")
    new_user = create_user("newuser", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=new_user, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # Team admin can add member
    response = client.post(
        f"/api/teams/{team.id}/members",
        json={"username": "newuser"},
        headers=get_auth_headers(team_admin)
    )
    assert response.status_code == 200

    # Team member cannot add
    response = client.post(
        f"/api/teams/{team.id}/members",
        json={"username": "teammember"},
        headers=get_auth_headers(team_member)
    )
    assert response.status_code == 403


def test_add_team_member_requires_org_membership(client, test_db):
    """Adding to team requires user to be org member first"""
    team_admin = create_user("teamadmin", "password")
    outsider = create_user("outsider", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    # outsider is NOT an org member

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))

    # Cannot add non-org-member to team
    response = client.post(
        f"/api/teams/{team.id}/members",
        json={"username": "outsider"},
        headers=get_auth_headers(team_admin)
    )
    assert response.status_code == 400


def test_list_team_members_requires_org_membership(client, test_db):
    """Listing team members requires being an org member"""
    user1 = create_user("user1", "password")
    user2 = create_user("user2", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=user1, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=user1, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # user1 (org member) can list
    response = client.get(f"/api/teams/{team.id}/members", headers=get_auth_headers(user1))
    assert response.status_code == 200
    assert len(response.json()) == 1

    # user2 (not org member) cannot list
    response = client.get(f"/api/teams/{team.id}/members", headers=get_auth_headers(user2))
    assert response.status_code == 403


def test_update_team_member_role_requires_team_admin(client, test_db):
    """Updating team member role requires team admin"""
    team_admin = create_user("teamadmin", "password")
    team_member = create_user("teammember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))
    team_member_record = TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # Team admin can update
    response = client.put(
        f"/api/teams/{team.id}/members/{team_member.id}",
        json={"role": "admin"},
        headers=get_auth_headers(team_admin)
    )
    assert response.status_code == 200

    # Team member cannot update
    response = client.put(
        f"/api/teams/{team.id}/members/{team_admin.id}",
        json={"role": "member"},
        headers=get_auth_headers(team_member)
    )
    assert response.status_code == 403


def test_remove_team_member_permissions(client, test_db):
    """Removing team member: admin can remove others, anyone can remove self"""
    team_admin = create_user("teamadmin", "password")
    team_member = create_user("teammember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))
    team_member_record = TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # Team admin can remove member
    response = client.delete(
        f"/api/teams/{team.id}/members/{team_member.id}",
        headers=get_auth_headers(team_admin)
    )
    assert response.status_code == 200


def test_remove_team_member_can_remove_self(client, test_db):
    """Team member can remove themselves"""
    team_admin = create_user("teamadmin", "password")
    team_member = create_user("teammember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_admin, organization=org, role="member", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_admin, team=team, role="admin", joined_at=datetime.now(timezone.utc))
    team_member_record = TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    # Member can remove self
    response = client.delete(
        f"/api/teams/{team.id}/members/{team_member.id}",
        headers=get_auth_headers(team_member)
    )
    assert response.status_code == 200


# ===============================
# BOARD PERMISSION TESTS
# ===============================

def test_share_board_requires_owner(client, test_db):
    """Sharing a board requires being a board owner"""
    owner = create_user("owner", "password")
    other_user = create_user("other", "password")

    board = Board.create_with_columns(owner=owner, name="My Board")

    # Owner can share
    response = client.post(
        f"/api/boards/{board.id}/share",
        json={"team_id": None},
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Other user cannot share
    response = client.post(
        f"/api/boards/{board.id}/share",
        json={"team_id": None},
        headers=get_auth_headers(other_user)
    )
    assert response.status_code == 403


def test_board_access_through_team_sharing(client, test_db):
    """Board shared with team is accessible to team members"""
    owner = create_user("owner", "password")
    team_member = create_user("teammember", "password")
    non_member = create_user("nonmember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    board = Board.create_with_columns(owner=owner, name="Shared Board", shared_team=team)

    # Owner can access
    response = client.get(f"/api/boards/{board.id}", headers=get_auth_headers(owner))
    assert response.status_code == 200

    # Team member can access
    response = client.get(f"/api/boards/{board.id}", headers=get_auth_headers(team_member))
    assert response.status_code == 200

    # Non-member cannot access
    response = client.get(f"/api/boards/{board.id}", headers=get_auth_headers(non_member))
    assert response.status_code == 403


def test_update_board_requires_owner_or_team_member(client, test_db):
    """Updating board requires owner or team member"""
    owner = create_user("owner", "password")
    team_member = create_user("teammember", "password")
    other_user = create_user("other", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    board = Board.create_with_columns(owner=owner, name="Shared Board", shared_team=team)

    # Owner can update
    response = client.post(
        f"/api/boards/{board.id}",
        json={"name": "Updated"},
        headers=get_auth_headers(owner)
    )
    assert response.status_code == 200

    # Team member can update
    response = client.post(
        f"/api/boards/{board.id}",
        json={"name": "Updated"},
        headers=get_auth_headers(team_member)
    )
    assert response.status_code == 200

    # Other user cannot update
    response = client.post(
        f"/api/boards/{board.id}",
        json={"name": "Should Not Update"},
        headers=get_auth_headers(other_user)
    )
    assert response.status_code == 403


def test_delete_board_requires_owner(client, test_db):
    """Deleting a board requires being a board owner"""
    owner = create_user("owner", "password")
    team_member = create_user("teammember", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    board = Board.create_with_columns(owner=owner, name="Shared Board", shared_team=team)

    # Owner can delete
    response = client.delete(f"/api/boards/{board.id}", headers=get_auth_headers(owner))
    assert response.status_code == 200

    # Create another board for team member test
    board2 = Board.create_with_columns(owner=owner, name="Shared Board 2", shared_team=team)

    # Team member cannot delete
    response = client.delete(f"/api/boards/{board2.id}", headers=get_auth_headers(team_member))
    assert response.status_code == 403


def test_list_boards_includes_shared_boards(client, test_db):
    """Listing boards includes both owned and shared boards"""
    owner = create_user("owner", "password")
    team_member = create_user("teammember", "password")
    other_user = create_user("other", "password")

    org = Organization.create(name="Org1", slug="org1", created_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=owner, organization=org, role="owner", joined_at=datetime.now(timezone.utc))
    OrganizationMember.create(user=team_member, organization=org, role="member", joined_at=datetime.now(timezone.utc))

    team = Team.create(name="Team1", organization=org, created_at=datetime.now(timezone.utc))
    TeamMember.create(user=team_member, team=team, role="member", joined_at=datetime.now(timezone.utc))

    board1 = Board.create_with_columns(owner=owner, name="Owned Board")
    board2 = Board.create_with_columns(owner=owner, name="Shared Board", shared_team=team)

    # Owner sees both boards
    response = client.get("/api/boards", headers=get_auth_headers(owner))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Team member sees only shared board
    response = client.get("/api/boards", headers=get_auth_headers(team_member))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == board2.id

    # Other user sees no boards
    response = client.get("/api/boards", headers=get_auth_headers(other_user))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
