# Production Deployment Guide

This guide will help you deploy the Kanban Board application to production on an Ubuntu LTS server with nginx.

## Prerequisites

- Ubuntu LTS server with root/sudo access
- Domain name `kanban.pearachute.com` pointing to your server
- Git installed

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/pearachute/kanban.git /opt/kanban
   cd /opt/kanban
   ```

2. Make scripts executable:
   ```bash
   chmod +x sys/scripts/*.sh
   ```

3. Run the deployment script:
   ```bash
   sudo sys/scripts/deploy.sh
   ```

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. System Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx git
```

### 2. Application User

```bash
# Create system user
sudo useradd --system --home /opt/kanban --shell /bin/bash kanban

# Create directories
sudo mkdir -p /opt/kanban/{data,logs}
sudo mkdir -p /var/www/certbot
sudo chown -R kanban:kanban /opt/kanban
```

### 3. Application Setup

```bash
# Clone repository
sudo -u kanban git clone https://github.com/pearachute/kanban.git /opt/kanban

# Setup virtual environment
sudo -u kanban python3 -m venv /opt/kanban/venv

# Install Python dependencies
sudo -u kanban /opt/kanban/venv/bin/pip install --upgrade pip
sudo -u kanban /opt/kanban/venv/bin/pip install -r /opt/kanban/backend/requirements.txt

# Build frontend
sudo -u kanban bash -c "cd /opt/kanban/frontend && npm install && npm run build"
```

### 4. Database Setup

```bash
# Initialize database
sudo -u kanban /opt/kanban/venv/bin/python /opt/kanban/manage.py init

# Create admin user
sudo -u kanban /opt/kanban/venv/bin/python /opt/kanban/manage.py user-create admin yourpassword --admin
```

### 5. Systemd Service

```bash
# Copy service file
sudo cp /opt/kanban/sys/systemd/kanban.service /etc/systemd/system/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable kanban
sudo systemctl start kanban
```

### 6. Nginx Configuration

```bash
# Copy nginx config
sudo cp /opt/kanban/sys/nginx/kanban.pearachute.com.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/kanban.pearachute.com.conf /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate

```bash
# Run SSL setup script
sudo /opt/kanban/sys/scripts/setup-ssl.sh

# Or manually:
sudo certbot --nginx -d kanban.pearachute.com
```

## Configuration

### Environment Variables

Copy the environment template and customize:

```bash
sudo -u kanban cp /opt/kanban/sys/config/production.env /opt/kanban/.env
```

Edit `/opt/kanban/.env` to configure:
- Database path
- JWT secret key (change this!)
- CORS origins
- Email settings (optional)

### Service Management

```bash
# Check service status
sudo systemctl status kanban

# View logs
sudo journalctl -u kanban -f

# Restart service
sudo systemctl restart kanban

# Stop service
sudo systemctl stop kanban
```

## Maintenance

### Updates

To update the application:

```bash
# Pull latest changes
cd /opt/kanban
sudo -u kanban git pull

# Rebuild frontend (if needed)
sudo -u kanban bash -c "cd frontend && npm install && npm run build"

# Restart service
sudo systemctl restart kanban
```

### Database Management

```bash
# Check database status
sudo -u kanban /opt/kanban/venv/bin/python /opt/kanban/manage.py status

# Backup database
sudo cp /opt/kanban/data/kanban.db /opt/kanban/data/kanban.db.backup.$(date +%Y%m%d)
```

### SSL Certificate Renewal

Let's Encrypt certificates are automatically renewed via cron. To test renewal:

```bash
sudo certbot renew --dry-run
```

## Troubleshooting

### Service Won't Start

Check logs for errors:
```bash
sudo journalctl -u kanban -f
```

Common issues:
- Missing dependencies: `sudo -u kanban /opt/kanban/venv/bin/pip install -r backend/requirements.txt`
- Permissions: Ensure `/opt/kanban` is owned by `kanban` user
- Database: Run `sudo -u kanban /opt/kanban/venv/bin/python /opt/kanban/manage.py init`

### Nginx Issues

Test nginx configuration:
```bash
sudo nginx -t
```

Check nginx logs:
```bash
sudo tail -f /var/log/nginx/kanban.pearachute.com.error.log
```

### SSL Issues

Check certificate status:
```bash
sudo certbot certificates
```

Request new certificate:
```bash
sudo certbot --nginx -d kanban.pearachute.com --force-renewal
```

## Security Considerations

1. **Change JWT Secret**: Always change the JWT secret key in production
2. **Regular Updates**: Keep system packages updated
3. **Backups**: Regularly backup the SQLite database
4. **Firewall**: Configure UFW or similar firewall
5. **Monitoring**: Set up monitoring for service health

## Performance Tuning

For higher traffic scenarios, consider:

1. **Process Management**: Use gunicorn with uvicorn workers instead of uvicorn directly
2. **Database**: Migrate to PostgreSQL for better performance
3. **Caching**: Add Redis caching for frequently accessed data
4. **CDN**: Use CDN for static assets

## Directory Structure

```
/opt/kanban/
├── backend/                 # FastAPI backend
├── frontend/                # Svelte frontend
├── sys/                     # Deployment configuration
│   ├── nginx/              # Nginx configs
│   ├── systemd/            # Service files
│   ├── scripts/            # Deployment scripts
│   └── config/             # Environment configs
├── data/                   # Database files
├── venv/                   # Python virtual environment
└── .env                    # Environment variables
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review service logs: `sudo journalctl -u kanban`
3. Review nginx logs: `sudo tail -f /var/log/nginx/kanban.pearachute.com.error.log`
4. Check the GitHub repository for known issues