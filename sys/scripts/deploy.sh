#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/kanban"

# The commit the server was on before this deploy pulled. Change detection has
# to compare against it rather than HEAD~1: a push of several commits moves
# HEAD by more than one, so HEAD~1 sees only the final commit of the push. A
# requirements.txt change in any earlier commit was invisible, and the service
# restarted without its new dependencies.
PREVIOUS_SHA=""

# Did anything matching $1 change between the pre-deploy commit and now?
changed_since_previous() {
    if [ -z "$PREVIOUS_SHA" ]; then
        # No baseline to compare against, so do the work rather than silently
        # skip it -- a needless pip install is cheap, a missing one is not.
        return 0
    fi
    git diff --name-only "$PREVIOUS_SHA" HEAD | grep -q "$1"
}

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

    # Captured before the reset, so change detection can see the whole push.
    PREVIOUS_SHA=$(git rev-parse HEAD)

    git fetch origin
    git reset --hard origin/$CURRENT_BRANCH

    echo "Code updated ($PREVIOUS_SHA -> $(git rev-parse HEAD))"
}

# Function to update dependencies
update_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

    # Keep this ahead of run_migrations: the migration runner imports
    # peewee-migrate, so the deploy that introduces a dependency has to install
    # it before the step that needs it.
    #
    # Gating here is sound now that changed_since_previous() compares against
    # the pre-pull SHA. It was not when the comparison was `HEAD~1 HEAD`, which
    # saw only the final commit of a push.
    if changed_since_previous "backend/requirements.txt"; then
        echo "Requirements changed, updating..."
        $DEPLOY_DIR/venv/bin/pip install -r $DEPLOY_DIR/backend/requirements.txt
    else
        echo "Requirements unchanged, skipping"
    fi
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

    # Deliberately NOT gated on changed_since_previous, unlike the pip step
    # above. That helper answers "did migration files change in this push",
    # but the question that matters is "does this database have unapplied
    # migrations" -- and only the migratehistory table knows. A deploy that
    # failed partway, a rollback and re-deploy, or a database restored from an
    # older backup all leave migrations pending with no diff to detect them.
    # peewee-migrate skips what it has already applied, so always asking costs
    # one query.
    #
    # This must happen before restart_service. The old code is still serving
    # traffic at this point and does not know about the new columns, so
    # migrating first means the new code never starts against an old schema.
    cd $DEPLOY_DIR

    # Migrate the database the SERVICE uses, which is not necessarily the one
    # manage.py would pick on its own. systemd sets DATABASE_PATH from
    # /opt/kanban/.env (EnvironmentFile) falling back to the Environment= line
    # in kanban.service; this shell has neither, so without the lookup below
    # manage.py defaults to ./kanban.db and would happily migrate the wrong
    # file -- leaving the live database untouched and unmigrated.
    #
    # Read rather than sourced: .env is systemd-format, where values are
    # literal to end of line, so `RESEND_FROM=Kanban <noreply@...>` is valid
    # there but would be a redirect to bash.
    DB_PATH=""
    if [ -f "$DEPLOY_DIR/.env" ]; then
        DB_PATH=$(grep -E '^[[:space:]]*DATABASE_PATH=' "$DEPLOY_DIR/.env" \
            | tail -1 | cut -d= -f2- | tr -d '"'"'"'' | xargs)
    fi
    # Matches Environment=DATABASE_PATH in sys/systemd/kanban.service.
    DB_PATH="${DB_PATH:-$DEPLOY_DIR/kanban.db}"

    echo "Target database: $DB_PATH"
    DATABASE_PATH="$DB_PATH" $DEPLOY_DIR/venv/bin/python manage.py migrate

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
