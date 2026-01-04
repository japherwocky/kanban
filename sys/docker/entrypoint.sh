#!/bin/bash

set -e

echo "🚀 Starting Kanban Board container initialization..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if database is initialized
is_db_initialized() {
    if [ -f "$DATABASE_PATH" ]; then
        # Check if database has any tables
        python -c "
import sys
sys.path.append('/opt/kanban')
from backend.database import db
from backend.models import User
try:
    db.connect()
    count = User.select().count()
    db.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null
        return $?
    else
        return 1
    fi
}

# Function to initialize database
init_database() {
    echo -e "${YELLOW}🗄️ Initializing database...${NC}"
    /opt/kanban/venv/bin/python manage.py init
    echo -e "${GREEN}✅ Database initialized${NC}"
}

# Function to create admin user
create_admin_user() {
    echo -e "${YELLOW}👔 Creating admin user...${NC}"
    
    # Use environment variables for admin credentials or defaults
    ADMIN_USER=${ADMIN_USER:-admin}
    ADMIN_PASS=${ADMIN_PASS:-admin123}
    
    echo "Creating admin user: $ADMIN_USER"
    
    /opt/kanban/venv/bin/python manage.py user-create "$ADMIN_USER" "$ADMIN_PASS" --admin
    echo -e "${GREEN}✅ Admin user created successfully${NC}"
    echo -e "${YELLOW}⚠️  Remember to change the default password!${NC}"
}

# Main initialization logic
if ! is_db_initialized; then
    echo -e "${GREEN}First run detected - initializing application...${NC}"
    init_database
    create_admin_user
    echo -e "${GREEN}🎉 Initialization complete!${NC}"
else
    echo -e "${GREEN}✅ Database already initialized${NC}"
fi

# Create necessary directories and set permissions
mkdir -p /var/log/supervisor
mkdir -p /var/log/nginx
mkdir -p /tmp/nginx

# Set correct ownership (run as root for system directories)
chown -R kanban:kanban /opt/kanban
chown -R kanban:kanban /var/log/supervisor
chown -R nginx:nginx /var/log/nginx
chown -R nginx:nginx /tmp/nginx

echo -e "${GREEN}🚀 Ready to start services...${NC}"

# Start supervisord in the background to let the container continue
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf