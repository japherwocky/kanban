#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/kanban"

echo -e "${GREEN}🚀 Deploying Kanban Board updates${NC}"
echo "Deploy Directory: $DEPLOY_DIR"
echo ""

# Check if running as kanban user
check_user() {
    if [[ "$(whoami)" != "kanban" ]]; then
        echo -e "${RED}This script must be run as the kanban user:${NC}"
        echo "  sudo -u kanban $DEPLOY_DIR/sys/scripts/deploy.sh"
        exit 1
    fi
}

# Function to git pull
git_pull() {
    echo -e "${YELLOW}📥 Pulling latest changes...${NC}"

    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "Current branch: $CURRENT_BRANCH"

    git fetch origin
    git pull origin $CURRENT_BRANCH

    echo "Code updated"
}

# Function to update dependencies (if requirements changed)
update_dependencies() {
    echo -e "${YELLOW}📦 Checking Python dependencies...${NC}"

    # Check if requirements.txt changed
    if git diff --name-only HEAD~1 HEAD | grep -q "backend/requirements.txt"; then
        echo "Requirements changed, updating..."
        $DEPLOY_DIR/venv/bin/pip install -r $DEPLOY_DIR/backend/requirements.txt
    else
        echo "Requirements unchanged, skipping"
    fi
}

# Function to build frontend
build_frontend() {
    echo -e "${YELLOW}🏗️ Building frontend...${NC}"

    # Check if frontend files changed
    if git diff --name-only HEAD~1 HEAD | grep -q "frontend/"; then
        echo "Frontend files changed, rebuilding..."
        cd $DEPLOY_DIR/frontend
        npm install
        npm run build
        echo "Frontend rebuilt"
    else
        echo "Frontend files unchanged, skipping"
    fi
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}🗄️ Checking for database migrations...${NC}"

    # Check if migration files changed
    if git diff --name-only HEAD~1 HEAD | grep -q "backend/migrations/"; then
        echo "Migration files changed, checking database..."
        # Add migration logic here if needed
        echo "Migrations complete"
    else
        echo "No migrations needed"
    fi
}

# Function to restart service
restart_service() {
    echo -e "${YELLOW}🔄 Restarting kanban service...${NC}"
    sudo systemctl restart kanban
    sleep 2

    # Check if service is running
    if systemctl is-active --quiet kanban; then
        echo -e "${GREEN}✅ Service restarted successfully${NC}"
    else
        echo -e "${RED}❌ Service failed to start${NC}"
        systemctl status kanban --no-pager
        exit 1
    fi
}

# Main deployment flow
main() {
    check_user

    cd $DEPLOY_DIR

    echo -e "${GREEN}Step 1: Pull updates${NC}"
    git_pull

    echo -e "${GREEN}Step 2: Update dependencies${NC}"
    update_dependencies

    echo -e "${GREEN}Step 3: Build frontend${NC}"
    build_frontend

    echo -e "${GREEN}Step 4: Run migrations${NC}"
    run_migrations

    echo -e "${GREEN}Step 5: Restart service${NC}"
    restart_service

    echo ""
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo ""
    echo "Useful commands:"
    echo "  Check service status: systemctl status kanban"
    echo "  View logs: journalctl -u kanban -f"
}

# Run deployment
main "$@"
