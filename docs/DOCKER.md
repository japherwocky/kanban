# Docker Development Setup

This directory contains Docker configuration for running the Kanban Board application in a container that mirrors the production VPS setup.

## Architecture

The Docker container replicates the production environment:

- **Ubuntu 22.04** base image (matches production server)
- **Supervisord** process manager (replaces systemd)
- **Nginx** reverse proxy (HTTP only for local testing)
- **FastAPI** backend with Uvicorn
- **SQLite** database (persistent via volume)
- **Svelte** frontend (built during container build)

## Quick Start

### 1. Build the Docker Image

```bash
# Build from the current directory
docker build -t kanban:latest .

# Or build with custom tag
docker build -t kanban:dev .
```

### 2. Run the Container

```bash
# Basic run (creates database in container, lost on container removal)
docker run -d -p 8080:80 --name kanban kanban:latest

# Recommended: Persistent database and logs
docker run -d \
  -p 8080:80 \
  -v kanban-data:/opt/kanban/data \
  -v kanban-logs:/var/log \
  --name kanban \
  kanban:latest
```

### 3. Access the Application

- **URL**: http://localhost:8080
- **Default Admin**: `admin` / `admin123`

## Configuration

### Environment Variables

You can customize the container using environment variables:

```bash
docker run -d \
  -p 8080:80 \
  -e ADMIN_USER=myadmin \
  -e ADMIN_PASS=mypassword \
  -e JWT_SECRET_KEY=my-secret-key \
  -v kanban-data:/opt/kanban/data \
  --name kanban \
  kanban:latest
```

Available environment variables:
- `ADMIN_USER`: Admin username (default: `admin`)
- `ADMIN_PASS`: Admin password (default: `admin123`)
- `JWT_SECRET_KEY`: JWT signing secret (change in production!)
- `DATABASE_PATH`: SQLite database path
- `STATIC_PATH`: Frontend static files path
- `LOG_LEVEL`: Logging level (debug, info, warning, error)
- `CORS_ORIGINS`: Allowed CORS origins

### Custom Environment File

Create a custom `.env` file and mount it:

```bash
# Create your env file
cat > my-docker.env << EOF
ADMIN_USER=myuser
ADMIN_PASS=mypassword
JWT_SECRET_KEY=my-very-secure-secret
LOG_LEVEL=debug
EOF

# Run with custom env
docker run -d \
  -p 8080:80 \
  --env-file my-docker.env \
  -v kanban-data:/opt/kanban/data \
  --name kanban \
  kanban:latest
```

## Development Workflow

### Rebuilding the Container

After making changes to code:

```bash
# Stop and remove old container
docker stop kanban
docker rm kanban

# Rebuild image (Dockerfile changes or new dependencies)
docker build -t kanban:latest .

# Run new container
docker run -d -p 8080:80 -v kanban-data:/opt/kanban/data --name kanban kanban:latest
```

### Frontend Development

For frontend development with hot reload, use the local development setup instead of Docker:

```bash
cd frontend
npm install
npm run dev
```

The Docker setup is intended for testing the production-like deployment.

### Backend Development

For backend development with hot reload:

```bash
cd backend
pip install -r requirements.txt
cd ..
python manage.py server --reload
```

## Container Management

### View Logs

```bash
# Container logs
docker logs kanban

# Follow logs
docker logs -f kanban

# Service-specific logs
docker exec kanban tail -f /var/log/supervisor/fastapi.log
docker exec kanban tail -f /var/log/supervisor/nginx.log
```

### Access Container Shell

```bash
docker exec -it kanban /bin/bash
```

### Database Management

```bash
# Database status
docker exec kanban /opt/kanban/venv/bin/python manage.py status

# Create new user
docker exec kanban /opt/kanban/venv/bin/python manage.py user-create newuser password123

# Initialize/reset database (DESTRUCTIVE)
docker exec kanban /opt/kanban/venv/bin/python manage.py wipe
```

### Stop and Start

```bash
# Stop
docker stop kanban

# Start
docker start kanban

# Remove (database volume will be preserved)
docker rm kanban
```

## Volume Management

### Database Backup

```bash
# Backup database
docker run --rm -v kanban-data:/data -v $(pwd):/backup alpine \
  cp /data/kanban.db /backup/kanban-backup-$(date +%Y%m%d).db

# Restore database
docker run --rm -v kanban-data:/data -v $(pwd):/backup alpine \
  cp /backup/kanban-backup.db /data/kanban.db
```

### Clean Up Volumes

```bash
# List volumes
docker volume ls

# Remove volume (DELETES ALL DATA)
docker volume rm kanban-data kanban-logs
```

## Production Deployment

The Docker container is designed to closely match the production setup. For actual production deployment:

1. **Use the production deployment scripts** in `sys/scripts/deploy.sh`
2. **Change default secrets**: JWT_SECRET_KEY, admin password
3. **Enable SSL**: Use the production nginx configuration with Let's Encrypt
4. **Monitor**: Set up monitoring and log aggregation
5. **Backups**: Regular database backups

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs kanban

# Check if port is in use
netstat -tulpn | grep 8080

# Check container status
docker ps -a
```

### Database Issues

```bash
# Check database directory permissions
docker exec kanban ls -la /opt/kanban/data/

# Reinitialize database
docker exec kanban /opt/kanban/venv/bin/python manage.py wipe
```

### Frontend Not Loading

```bash
# Check if static files exist
docker exec kanban ls -la /opt/kanban/backend/static/

# Check nginx logs
docker exec kanban tail -f /var/log/nginx/error.log
```

### Performance Issues

```bash
# Monitor resource usage
docker stats kanban

# Check processes
docker exec kanban ps aux
```

## Security Notes

- The container runs as non-root user `kanban` where possible
- Default credentials (`admin`/`admin123`) are for testing only
- JWT secret key should be changed in production
- SSL is disabled for local testing - enable for production
- Database is exposed only within the container

## Differences from Production

| Feature | Production | Docker |
|---------|------------|--------|
| SSL | Yes (Let's Encrypt) | No (HTTP only) |
| Process Manager | systemd | supervisord |
| Base OS | Ubuntu LTS | Ubuntu 22.04 |
| Auto-admin | Manual creation | Automatic on first run |
| Logs | systemd journal | File logs + supervisor |
| Database | `/opt/kanban/data/` | Volume mounted |

This setup is designed for testing the deployment configuration before deploying to the VPS.