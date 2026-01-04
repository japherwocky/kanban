# Multi-stage Dockerfile for Kanban Board
# Stage 1: Frontend Build (Node.js)
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci --only=production

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Container (Ubuntu + Python)
FROM ubuntu:22.04

# Set environment to non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /opt/kanban

# Create data directory for SQLite database
RUN mkdir -p /opt/kanban/data

# Set up Python virtual environment
RUN python3.10 -m venv /opt/kanban/venv
ENV PATH="/opt/kanban/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY manage.py .
COPY sys/docker/entrypoint.sh ./
COPY sys/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy built frontend files
COPY --from=frontend-builder /app/frontend/build ./backend/static/

# Copy nginx configuration
COPY sys/docker/nginx.conf /etc/nginx/sites-available/kanban

# Enable nginx site
RUN rm /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/kanban /etc/nginx/sites-enabled/

# Make scripts executable
RUN chmod +x entrypoint.sh

# Create non-root user (matches production security)
RUN useradd --system --home /opt/kanban --shell /bin/bash kanban && \
    chown -R kanban:kanban /opt/kanban

# Expose HTTP port
EXPOSE 80

# Switch to non-root user for application
USER kanban

# Set environment variables
ENV DATABASE_PATH=/opt/kanban/data/kanban.db
ENV STATIC_PATH=/opt/kanban/backend/static
ENV APP_HOST=127.0.0.1
ENV APP_PORT=8000
ENV JWT_SECRET_KEY=change-this-secret-key-in-production
ENV JWT_ALGORITHM=HS256
ENV JWT_EXPIRE_MINUTES=30
ENV LOG_LEVEL=info
ENV CORS_ORIGINS=*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]