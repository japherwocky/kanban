#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER="kanban"
DEPLOY_DIR="/opt/kanban"
SERVICE_NAME="kanban"
DOMAIN="kanban.pearachute.com"

echo -e "${GREEN}🚀 Deploying Kanban Board to production${NC}"
echo "Domain: $DOMAIN"
echo "Deploy Directory: $DEPLOY_DIR"
echo "Service: $SERVICE_NAME"
echo ""

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root (use sudo)${NC}"
        exit 1
    fi
}

# Function to create user if not exists
create_user() {
    echo -e "${YELLOW}👤 Creating deployment user...${NC}"
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd --system --home $DEPLOY_DIR --shell /bin/bash $DEPLOY_USER
        echo "User $DEPLOY_USER created"
    else
        echo "User $DEPLOY_USER already exists"
    fi
}

# Function to create directories
create_directories() {
    echo -e "${YELLOW}📁 Creating directories...${NC}"
    mkdir -p $DEPLOY_DIR/{data,logs}
    mkdir -p /var/www/certbot
    chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR
}

# Function to setup virtual environment
setup_virtualenv() {
    echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
    sudo -u $DEPLOY_USER python3 -m venv $DEPLOY_DIR/venv
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
    apt-get update
    apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx

    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    sudo -u $DEPLOY_USER $DEPLOY_DIR/venv/bin/pip install --upgrade pip
    sudo -u $DEPLOY_USER $DEPLOY_DIR/venv/bin/pip install -r $DEPLOY_DIR/backend/requirements.txt
}

# Function to build frontend
build_frontend() {
    echo -e "${YELLOW}🏗️ Building frontend...${NC}"
    sudo -u $DEPLOY_USER bash -c "cd $DEPLOY_DIR/frontend && npm install"
    sudo -u $DEPLOY_USER bash -c "cd $DEPLOY_DIR/frontend && npm run build"
}

# Function to setup database
setup_database() {
    echo -e "${YELLOW}🗄️ Setting up database...${NC}"
    if [ ! -f "$DEPLOY_DIR/data/kanban.db" ]; then
        sudo -u $DEPLOY_USER $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/manage.py init
        echo "Database initialized"
    else
        echo "Database already exists"
    fi
}

# Function to setup systemd service
setup_systemd() {
    echo -e "${YELLOW}⚙️ Setting up systemd service...${NC}"
    cp $DEPLOY_DIR/sys/systemd/kanban.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable kanban
}

# Function to setup nginx
setup_nginx() {
    echo -e "${YELLOW}🌐 Setting up nginx...${NC}"
    cp $DEPLOY_DIR/sys/nginx/kanban.pearachute.com.conf /etc/nginx/sites-available/
    ln -sf /etc/nginx/sites-available/kanban.pearachute.com.conf /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
}

# Function to setup SSL with Let's Encrypt
setup_ssl() {
    echo -e "${YELLOW}🔒 Setting up SSL with Let's Encrypt...${NC}"
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo -e "${RED}SSL setup failed. You may need to run certbot manually:${NC}"
        echo "certbot --nginx -d $DOMAIN"
    }
}

# Function to create admin user
create_admin_user() {
    echo -e "${YELLOW}👔 Creating admin user...${NC}"
    read -p "Enter admin username: " ADMIN_USER
    read -s -p "Enter admin password: " ADMIN_PASS
    echo
    sudo -u $DEPLOY_USER $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/manage.py user-create $ADMIN_USER $ADMIN_PASS --admin
}

# Function to start service
start_service() {
    echo -e "${YELLOW}🚀 Starting kanban service...${NC}"
    systemctl start kanban
    systemctl status kanban --no-pager
}

# Main deployment flow
main() {
    check_root
    
    echo -e "${GREEN}Step 1: User and directories${NC}"
    create_user
    create_directories
    
    echo -e "${GREEN}Step 2: Application setup${NC}"
    setup_virtualenv
    install_dependencies
    build_frontend
    
    echo -e "${GREEN}Step 3: Database setup${NC}"
    setup_database
    
    echo -e "${GREEN}Step 4: Service configuration${NC}"
    setup_systemd
    setup_nginx
    
    echo -e "${GREEN}Step 5: SSL setup${NC}"
    setup_ssl
    
    echo -e "${GREEN}Step 6: Admin user${NC}"
    create_admin_user
    
    echo -e "${GREEN}Step 7: Start service${NC}"
    start_service
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo "Your Kanban board is now running at: https://$DOMAIN"
    echo ""
    echo "Useful commands:"
    echo "  Check service status: systemctl status kanban"
    echo "  View logs: journalctl -u kanban -f"
    echo "  Restart service: systemctl restart kanban"
    echo "  Update application: cd $DEPLOY_DIR && git pull && sudo systemctl restart kanban"
}

# Run deployment
main "$@"