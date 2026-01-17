# GitHub Actions Deployment Setup Guide

## Overview

This setup leverages your existing VPS configuration without storing any secrets in GitHub. The workflow simply SSH's into your server and runs the existing `deploy.sh` script.

## Prerequisites

You should already have:
✅ VPS with kanban user and SSH access  
✅ Working deployment at `/opt/kanban`  
✅ Functional `deploy.sh` script  
✅ Production `.env` file on server  

## One-Time GitHub Setup

### 1. Create SSH Deploy Key

On your local machine (not the VPS):
```bash
# Generate a new SSH key for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/kanban-deploy

# This creates:
# - Private key: ~/.ssh/kanban-deploy
# - Public key:  ~/.ssh/kanban-deploy.pub
```

### 2. Add Public Key to VPS

Add the public key to the kanban user's authorized_keys on your VPS:

```bash
# Copy the public key content
cat ~/.ssh/kanban-deploy.pub

# On the VPS, add it to authorized_keys
sudo -u kanban mkdir -p /opt/kanban/.ssh
sudo -u kanban bash -c 'cat >> /opt/kanban/.ssh/authorized_keys' << 'EOF'
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... github-actions-deploy
EOF

# Set proper permissions
sudo -u kanban chmod 600 /opt/kanban/.ssh/authorized_keys
sudo -u kanban chmod 700 /opt/kanban/.ssh
```

### 3. Add Private Key to GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `DEPLOY_SSH_KEY`
5. Value: Content of `~/.ssh/kanban-deploy` (the private key)

```bash
# Copy the private key content
cat ~/.ssh/kanban-deploy
```

### 4. (Optional) Add Deploy Key to GitHub Repo

For additional security, you can also add this as a deploy key:

1. Settings → Deploy keys → Add deploy key
2. Title: "GitHub Actions Deploy"
3. Key: Paste the public key (`~/.ssh/kanban-deploy.pub`)
4. Check "Allow write access"

## Workflow Configuration

The workflow is now simplified to:
- Run tests on every push to main
- SSH into VPS using the deploy key
- Run the existing `sys/scripts/deploy.sh` script
- Verify deployment success

## Security Benefits

✅ **No production secrets in GitHub** - All secrets stay on VPS  
✅ **Minimal attack surface** - Only one SSH key as secret  
✅ **Existing infrastructure** - Uses your current setup  
✅ **Environment isolation** - Each environment manages its own config  
✅ **Easy to revoke** - Just remove the SSH key if compromised  

## Testing the Setup

1. Push a small change to main branch
2. Check GitHub Actions tab for deployment
3. Verify deployment succeeded on VPS

## Troubleshooting

### SSH Connection Issues
```bash
# Test SSH connection manually
ssh -i ~/.ssh/kanban-deploy kanban@kanban.pearachute.com
# Should connect without asking for password
```

### Permission Issues
Ensure the kanban user can run the deploy script:
```bash
# On VPS
sudo -u kanban /opt/kanban/sys/scripts/deploy.sh
```

### Deploy Script Issues
Check the deploy script logs on VPS:
```bash
# On VPS
sudo journalctl -u kanban -f
```

## Next Steps

Once this basic deployment is working, we can add:
1. Staging environment workflow
2. Backup automation
3. Health checks
4. Monitoring and alerts

But let's get this core deployment working first!