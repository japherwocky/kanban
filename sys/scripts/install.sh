#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_USER="kanban"
DEPLOY_DIR="/opt/kanban"
SOURCE_DIR="${SOURCE_DIR:-/tmp/kanban}"
SERVICE_NAME="kanban"
DOMAIN="kanban.pearachute.com"

echo -e "${GREEN}🚀 Installing Kanban Board to production${NC}"
echo "Source: $SOURCE_DIR"
echo "Deploy: $DEPLOY_DIR"
echo "Domain: $DOMAIN"
echo "User: $DEPLOY_USER"
echo ""

# Function to check if running as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo -e "${RED}This script must be run as root (use sudo)${NC}"
        exit 1
    fi
}

# Function to create user with SSH key
create_user() {
    echo -e "${YELLOW}👤 Creating deployment user with SSH key...${NC}"

    # Create user if not exists
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd --system --home $DEPLOY_DIR --shell /bin/bash $DEPLOY_USER
        echo "User $DEPLOY_USER created"
    else
        echo "User $DEPLOY_USER already exists"
    fi

    # Create .ssh directory
    mkdir -p $DEPLOY_DIR/.ssh
    chmod 700 $DEPLOY_DIR/.ssh
    chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR/.ssh

    # Generate SSH key if not exists
    SSH_KEY="$DEPLOY_DIR/.ssh/id_ed25519"
    if [ ! -f "$SSH_KEY" ]; then
        echo -e "${BLUE}🔑 Generating ED25519 SSH key for $DEPLOY_USER...${NC}"
        sudo -u $DEPLOY_USER ssh-keygen -t ed25519 -f $SSH_KEY -N "" -C "$DEPLOY_USER@$DOMAIN"
    else
        echo "SSH key already exists at $SSH_KEY"
    fi

    # Display public key (for adding to GitHub)
    echo ""
    echo -e "${GREEN}📋 Add this public key to GitHub as a deploy key:${NC}"
    echo ""
    cat $SSH_KEY.pub
    echo ""
}

# Function to copy repo from source
copy_repo() {
    echo -e "${YELLOW}📥 Copying repository from $SOURCE_DIR...${NC}"

    if [ ! -d "$SOURCE_DIR" ]; then
        echo -e "${RED}Source directory $SOURCE_DIR does not exist${NC}"
        exit 1
    fi

    if [ -d "$DEPLOY_DIR" ]; then
        echo "Removing existing $DEPLOY_DIR..."
        rm -rf $DEPLOY_DIR
    fi

    cp -r $SOURCE_DIR $DEPLOY_DIR
    chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR
    echo "Repository copied to $DEPLOY_DIR"
}

# Function to setup virtual environment
setup_virtualenv() {
    echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"

    if [ -f "$DEPLOY_DIR/venv/bin/python" ]; then
        echo "Virtualenv already exists"
    else
        sudo -u $DEPLOY_USER python3 -m venv $DEPLOY_DIR/venv
        echo "Virtualenv created"
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing system dependencies...${NC}"
    apt-get update
    apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git curl

    # Install Node.js 20 (required for frontend)
    echo -e "${YELLOW}📦 Installing Node.js 20...${NC}"
    if ! command -v node &>/dev/null || [ "$(node --version | cut -d'v' -f2 | cut -d'.' -f1)" -lt 20 ]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
        echo "Node.js $(node --version) installed"
    else
        echo "Node.js $(node --version) already installed"
    fi

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
        sudo -u $DEPLOY_USER DATABASE_PATH=$DEPLOY_DIR/data/kanban.db $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/manage.py init
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
    echo "Systemd service configured"
}

# Function to setup nginx
setup_nginx() {
    echo -e "${YELLOW}🌐 Setting up nginx...${NC}"
    cp $DEPLOY_DIR/sys/nginx/kanban.pearachute.com.conf /etc/nginx/sites-available/
    ln -sf /etc/nginx/sites-available/kanban.pearachute.com.conf /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
    echo "Nginx configured"
}

# Function to setup sudoers for kanban user
setup_sudoers() {
    echo -e "${YELLOW}🔐 Setting up sudoers permissions...${NC}"

    # Allow kanban user to restart the service without password
    echo "kanban ALL=(ALL) NOPASSWD: /bin/systemctl restart kanban" > /etc/sudoers.d/kanban-restart
    chmod 440 /etc/sudoers.d/kanban-restart

    echo "Sudoers configured - kanban can restart service without password"
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
    sudo -u $DEPLOY_USER DATABASE_PATH=$DEPLOY_DIR/data/kanban.db $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/manage.py user-create $ADMIN_USER $ADMIN_PASS --admin
}

# Function to start service
start_service() {
    echo -e "${GREEN}🚀 Starting kanban service...${NC}"
    systemctl start kanban
    systemctl status kanban --no-pager
}

# Main installation flow
main() {
    check_root

    echo -e "${GREEN}Step 1: User setup with SSH key${NC}"
    create_user

    echo -e "${GREEN}Step 2: Copy repository${NC}"
    copy_repo

    echo -e "${GREEN}Step 3: Application setup${NC}"
    setup_virtualenv
    install_dependencies
    build_frontend

    echo -e "${GREEN}Step 4: Database setup${NC}"
    setup_database

    echo -e "${GREEN}Step 5: Service configuration${NC}"
    setup_systemd
    setup_nginx
    setup_sudoers

    echo -e "${GREEN}Step 6: SSL setup${NC}"
    setup_ssl

    echo -e "${GREEN}Step 7: Admin user${NC}"
    create_admin_user

    echo -e "${GREEN}Step 8: Start service${NC}"
    start_service

    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Add the SSH public key above to GitHub as a deploy key"
    echo "2. Test deployment with: sudo -u kanban $DEPLOY_DIR/sys/scripts/deploy.sh"
    echo ""
    echo "Your Kanban board is now running at: https://$DOMAIN"
    echo ""
    echo "Useful commands:"
    echo "  Check service status: systemctl status kanban"
    echo "  View logs: journalctl -u kanban -f"
    echo "  Restart service: sudo systemctl restart kanban"
    echo "  Update application: sudo -u kanban $DEPLOY_DIR/sys/scripts/deploy.sh"
}

# Run installation
main "$@"
