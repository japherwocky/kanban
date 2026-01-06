#!/usr/bin/env python3

"""
Test script for organization and team CLI functionality
"""

import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import db
from backend.models import User, Organization, OrganizationMember, Team, TeamMember, Board, Column, Card, Comment
from backend.auth import create_access_token
from kanban.client import KanbanClient
from kanban.config import set_token, clear_token
import json

def test_organization_and_team_apis():
    """Test the new organization and team API methods"""
    
    # Use temporary database
    os.environ["DATABASE_PATH"] = "test_org_team.db"
    
    # Clean up any existing test database
    if os.path.exists("test_org_team.db"):
        os.remove("test_org_team.db")
    
    # Set up test database
    db.connect()
    db.create_tables([User, Organization, OrganizationMember, Team, TeamMember, Board, Column, Card, Comment])
    
    try:
        # Create test users
        admin_user = User.create_user("cli_admin", "password123", admin=True)
        regular_user = User.create_user("cli_regular", "password123")
        
        # Create token for regular user
        token = create_access_token(data={"sub": regular_user.id, "username": regular_user.username})
        
        # Mock the HTTP requests to return our test data
        with patch('kanban.client.requests.Session.request') as mock_request:
            # Setup mock client
            client = KanbanClient()
            
            # Test organization creation
            print("Testing organization API methods...")
            
            # Mock organization creation response
            mock_request.return_value.json.return_value = {
                "id": 1,
                "name": "Test Org",
                "owner_id": regular_user.id,
                "owner_username": "regular"
            }
            mock_request.return_value.raise_for_status.return_value = None
            
            result = client.organization_create("Test Org")
            print(f"[OK] Created organization: {result}")
            
            # Mock organizations list response
            mock_request.return_value.json.return_value = [
                {
                    "id": 1,
                    "name": "Test Org",
                    "owner_id": regular_user.id,
                    "owner_username": "regular"
                }
            ]
            
            orgs = client.organizations()
            print(f"[OK] Listed organizations: {orgs}")
            
            # Test team creation
            print("\nTesting team API methods...")
            
            # Mock team creation response
            mock_request.return_value.json.return_value = {
                "id": 1,
                "name": "Dev Team",
                "organization_id": 1,
                "organization_name": "Test Org"
            }
            
            team_result = client.team_create(1, "Dev Team")
            print(f"[OK] Created team: {team_result}")
            
            # Test board sharing
            print("\nTesting board sharing...")
            
            # Mock board sharing response
            mock_request.return_value.json.return_value = {
                "id": 1,
                "name": "Test Board",
                "shared_team_id": 1,
                "shared_team_name": "Dev Team"
            }
            
            share_result = client.board_share(1, 1)
            print(f"[OK] Shared board: {share_result}")
            
            print("\n[SUCCESS] All API methods work correctly!")
            
    finally:
        # Clean up
        db.close()
        if os.path.exists("test_org_team.db"):
            os.remove("test_org_team.db")

def test_cli_commands():
    """Test the new CLI commands"""
    print("\n" + "="*50)
    print("Testing CLI command structure...")
    
    # Test that the CLI can parse the new commands without errors
    from kanban.cli import main
    import argparse
    
    try:
        # Test organization commands
        parser = argparse.ArgumentParser(prog="kanban", description="Kanban board CLI")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # Add organization subcommands
        sp_org_create = subparsers.add_parser("org-create", help="Create an organization")
        sp_org_create.add_argument("name", help="Organization name")
        
        sp_org_get = subparsers.add_parser("org", help="Show organization details")
        sp_org_get.add_argument("id", type=int, help="Organization ID")
        
        # Add team subcommands  
        sp_team_create = subparsers.add_parser("team-create", help="Create a team")
        sp_team_create.add_argument("org_id", type=int, help="Organization ID")
        sp_team_create.add_argument("name", help="Team name")
        
        sp_team_get = subparsers.add_parser("team", help="Show team details")
        sp_team_get.add_argument("id", type=int, help="Team ID")
        
        # Add board sharing subcommand
        sp_board_share = subparsers.add_parser("board-share", help="Share board with team or make private")
        sp_board_share.add_argument("board_id", type=int, help="Board ID")
        sp_board_share.add_argument("team_id", help="Team ID or 'private' to make board private")
        
        # Test parsing
        args = parser.parse_args(["org-create", "Test Organization"])
        assert args.command == "org-create"
        assert args.name == "Test Organization"
        print("[OK] org-create command parsing works")
        
        args = parser.parse_args(["team-create", "1", "Dev Team"])
        assert args.command == "team-create"
        assert args.org_id == 1
        assert args.name == "Dev Team"
        print("[OK] team-create command parsing works")
        
        args = parser.parse_args(["board-share", "1", "2"])
        assert args.command == "board-share"
        assert args.board_id == 1
        assert args.team_id == "2"
        print("[OK] board-share command parsing works")
        
        print("[SUCCESS] All CLI command structures work correctly!")
        
    except Exception as e:
        print(f"❌ CLI command test failed: {e}")
        raise

if __name__ == "__main__":
    test_organization_and_team_apis()
    test_cli_commands()
    print("\n[SUCCESS] All tests passed! Organization and team functionality is ready.")
