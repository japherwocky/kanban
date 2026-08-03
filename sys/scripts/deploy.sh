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
    CURRENT_USER=$(whoami)
    if [ "$CURRENT_USER" != "kanban" ]; then
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
    git reset --hard origin/$CURRENT_BRANCH

    echo "Code updated"
}

# Function to update dependencies
update_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

    # Unconditional, for the same reason as run_migrations below. The old
    # `git diff HEAD~1 HEAD` guard only inspected the final commit of a push,
    # so a multi-commit push that touched requirements.txt in an earlier
    # commit skipped this entirely and left production missing a package.
    #
    # It also has to run before run_migrations: the migration runner imports
    # peewee-migrate, so gating this step would mean the very deploy that
    # introduces a dependency is the one that cannot use it.
    #
    # pip is a no-op when everything is already satisfied, so the cost of
    # running it every time is a few seconds.
    $DEPLOY_DIR/venv/bin/pip install -q -r $DEPLOY_DIR/backend/requirements.txt

    echo "Dependencies up to date"
}

# Function to build frontend
build_frontend() {
    echo -e "${YELLOW}🏗️ Building frontend...${NC}"

    cd $DEPLOY_DIR/frontend
    # Remove package-lock.json and node_modules to avoid native module issues
    rm -f package-lock.json
    rm -rf node_modules
    npm install
    npm run build
    echo "Frontend rebuilt"
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}🗄️ Running database migrations...${NC}"

    # Run unconditionally rather than gating on `git diff HEAD~1 HEAD`.
    # peewee-migrate records what it has applied and skips the rest, so an
    # up-to-date database costs one query. Gating on the diff was how this
    # step silently did nothing: it only ever inspected the final commit of a
    # push, and the body was a stub that printed success without running
    # anything.
    #
    # This must happen before restart_service. The old code is still serving
    # traffic at this point and does not know about the new columns, so
    # migrating first means the new code never starts against an old schema.
    cd $DEPLOY_DIR
    $DEPLOY_DIR/venv/bin/python manage.py migrate

    echo "Migrations complete"
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
