# 🚀 Production Deployment Guide

**Content Automation Platform - Production Deployment**

---

## 📋 Prerequisites

### Required
- ✅ Ubuntu 20.04+ or Debian 11+ server
- ✅ Docker 24.0+ and Docker Compose v2
- ✅ Minimum 4 GB RAM, 2 CPU cores
- ✅ 50 GB disk space
- ✅ Domain name with DNS access
- ✅ SSL certificate (Let's Encrypt auto-configured)

### Recommended
- 🎯 8 GB RAM, 4 CPU cores for production
- 🎯 100 GB SSD storage
- 🎯 CDN for static assets
- 🎯 Database backups to S3

---

## 🔧 Server Setup

### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verify
sudo ufw status
```

### 3. Optimize System

```bash
# Increase file limits
echo "fs.file-max = 2097152" | sudo tee -a /etc/sysctl.conf
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
sudo sysctl -p

# Enable swap (if RAM < 8GB)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📦 Application Deployment

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/eyeszik/full-stack-fastapi-template.git
cd full-stack-fastapi-template

# Checkout production branch
git checkout claude/content-autopilot-platform-dGBfJ
```

### Step 2: Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with your values
nano .env.production
```

**Required Configuration:**

```bash
# 1. Change security secrets
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

# 2. Set your domain
DOMAIN=yourdomain.com

# 3. Add API keys (get from respective platforms)
YOUTUBE_CLIENT_SECRET=xxx
FACEBOOK_APP_SECRET=xxx
LINKEDIN_CLIENT_SECRET=xxx
TWITTER_CLIENT_SECRET=xxx

# 4. Configure AWS S3
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=your-bucket

# 5. Add AI service keys (optional)
OPENAI_API_KEY=sk-xxx
# OR
ANTHROPIC_API_KEY=sk-ant-xxx

# 6. Configure email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 3: Configure DNS

Point your domain to the server:

```
Type: A Record
Name: @
Value: YOUR_SERVER_IP

Type: A Record
Name: *
Value: YOUR_SERVER_IP
```

This enables:
- `yourdomain.com` → Main app
- `grafana.yourdomain.com` → Monitoring
- `prometheus.yourdomain.com` → Metrics
- `traefik.yourdomain.com` → Load balancer

### Step 4: Deploy

```bash
# Make deployment script executable
chmod +x deploy/deploy.sh

# Run deployment
./deploy/deploy.sh production yourdomain.com
```

The script will:
1. ✅ Run pre-flight checks
2. ✅ Create Docker networks
3. ✅ Build images
4. ✅ Run database migrations
5. ✅ Start all services
6. ✅ Wait for health checks
7. ✅ Create superuser
8. ✅ Configure monitoring
9. ✅ Setup backups
10. ✅ Verify deployment

**Expected output:**
```
=================================================
Deployment Successful!
=================================================

🌐 Application: https://yourdomain.com
📊 Grafana: https://grafana.yourdomain.com
📈 Prometheus: https://prometheus.yourdomain.com
🔄 Traefik: https://traefik.yourdomain.com
```

---

## 🔍 Verification

### 1. Check Service Status

```bash
docker-compose -f docker-compose.prod.yml ps
```

All services should show "Up" and "healthy":

```
backend          Up (healthy)
frontend         Up (healthy)
db               Up (healthy)
redis            Up (healthy)
celery-worker    Up
celery-beat      Up
traefik          Up
prometheus       Up
grafana          Up
```

### 2. Test API

```bash
# Health check
curl https://yourdomain.com/api/v1/utils/health-check

# Expected: {"status":"ok"}

# API docs
curl https://yourdomain.com/docs
# Should return OpenAPI docs
```

### 3. Test SSL

```bash
# Check SSL certificate
curl -vI https://yourdomain.com 2>&1 | grep -i "subject:"

# Should show Let's Encrypt certificate
```

### 4. Login

```bash
# Open in browser
https://yourdomain.com

# Login with superuser credentials from .env.production
Email: admin@yourdomain.com
Password: [FIRST_SUPERUSER_PASSWORD]
```

---

## 📊 Monitoring

### Access Dashboards

1. **Grafana** (Metrics & Dashboards)
   - URL: `https://grafana.yourdomain.com`
   - User: Set in `.env.production` (`GRAFANA_USER`)
   - Password: Set in `.env.production` (`GRAFANA_PASSWORD`)

2. **Prometheus** (Metrics Database)
   - URL: `https://prometheus.yourdomain.com`
   - Direct metrics access

3. **Traefik** (Load Balancer Dashboard)
   - URL: `https://traefik.yourdomain.com`
   - Auth: Set in `.env.production` (`TRAEFIK_AUTH`)

### Key Metrics to Monitor

- **API Response Time** (p50, p95, p99)
- **Request Rate** (requests/sec)
- **Error Rate** (5xx responses)
- **Database Connections** (active, idle)
- **Celery Queue Length** (pending tasks)
- **Memory Usage** (per container)
- **CPU Usage** (per container)
- **Disk I/O** (read/write)

---

## 🔐 Security Checklist

### Pre-Launch

- [ ] Changed all default passwords
- [ ] Generated secure `SECRET_KEY` (min 32 chars)
- [ ] Configured firewall (UFW)
- [ ] SSL certificates installed
- [ ] CORS origins configured
- [ ] Rate limiting enabled
- [ ] API keys stored securely (not in git)
- [ ] Database password strong (min 16 chars)
- [ ] Redis password set
- [ ] Traefik dashboard password protected

### Post-Launch

- [ ] Enable Sentry error tracking
- [ ] Configure backup retention
- [ ] Test backup restoration
- [ ] Enable log rotation
- [ ] Configure alerts (email/Slack)
- [ ] Review access logs daily
- [ ] Update dependencies monthly
- [ ] Audit user permissions

---

## 🔄 Maintenance

### Daily Tasks

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Check disk space
df -h

# Monitor resource usage
docker stats
```

### Weekly Tasks

```bash
# Check for updates
docker-compose -f docker-compose.prod.yml pull

# Verify backups
ls -lh backups/

# Review error logs
docker-compose -f docker-compose.prod.yml logs backend | grep ERROR
```

### Monthly Tasks

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean Docker images
docker system prune -af

# Review security advisories
docker scan backend

# Update dependencies
cd backend && uv lock --upgrade
```

---

## 📈 Scaling

### Horizontal Scaling

Scale individual services:

```bash
# Scale backend API
docker-compose -f docker-compose.prod.yml up -d --scale backend=5

# Scale Celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4

# Scale frontend
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3
```

### Database Optimization

```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_content_owner_status ON content(owner_id, status);
CREATE INDEX idx_variant_published ON contentvariant(published_at);
CREATE INDEX idx_analytics_fetched ON contentanalytics(fetched_at);

-- Analyze tables
ANALYZE content, contentvariant, contentanalytics;
```

### Caching

Enable Redis caching:

```python
# In app/core/config.py
REDIS_CACHE_TTL = 300  # 5 minutes

# Cache API responses
@cache(expire=300)
def get_content_list():
    ...
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Common issues:
# 1. Port already in use
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# 2. Database connection failed
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.db import engine; engine.connect()"

# 3. Redis connection failed
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

### SSL Certificate Issues

```bash
# Check Traefik logs
docker-compose -f docker-compose.prod.yml logs traefik

# Force certificate renewal
docker-compose -f docker-compose.prod.yml exec traefik rm /acme.json
docker-compose -f docker-compose.prod.yml restart traefik
```

### High Memory Usage

```bash
# Identify container
docker stats --no-stream

# Restart service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Adjust limits in docker-compose.prod.yml
```

### Database Migration Failed

```bash
# Check current version
docker-compose -f docker-compose.prod.yml exec backend alembic current

# Rollback one version
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1

# Re-run migration
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 💾 Backup & Recovery

### Manual Backup

```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres content_automation > backup.sql

# Backup media files
tar -czf media-backup.tar.gz media/

# Upload to S3
aws s3 cp backup.sql s3://your-backup-bucket/backups/
aws s3 cp media-backup.tar.gz s3://your-backup-bucket/media/
```

### Automated Backups

Backups run daily at 3 AM via Celery Beat:

```bash
# Check backup logs
docker-compose -f docker-compose.prod.yml logs celery-beat | grep backup

# List backups
ls -lh backups/
aws s3 ls s3://your-backup-bucket/backups/
```

### Restore from Backup

```bash
# 1. Stop services
docker-compose -f docker-compose.prod.yml down

# 2. Restore database
docker-compose -f docker-compose.prod.yml up -d db
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres content_automation < backup.sql

# 3. Restore media
tar -xzf media-backup.tar.gz

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 Updates & Rollback

### Update Application

```bash
# 1. Pull latest code
git pull origin claude/content-autopilot-platform-dGBfJ

# 2. Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 4. Verify
curl https://yourdomain.com/api/v1/utils/health-check
```

### Rollback

```bash
# 1. Checkout previous version
git log --oneline  # Find commit hash
git checkout [commit-hash]

# 2. Rebuild
docker-compose -f docker-compose.prod.yml build

# 3. Rollback database
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1

# 4. Restart
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📞 Support

### Logs Location

- **Application Logs:** `logs/`
- **Traefik Logs:** `traefik/logs/`
- **Docker Logs:** `docker-compose -f docker-compose.prod.yml logs`

### Health Checks

```bash
# Backend API
curl https://yourdomain.com/api/v1/utils/health-check

# Database
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Celery
docker-compose -f docker-compose.prod.yml exec celery-worker celery -A app.worker inspect ping
```

### Performance Testing

```bash
# Load test with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/api/v1/utils/health-check

# Stress test
docker run --rm -it williamyeh/wrk -t4 -c100 -d30s https://yourdomain.com/
```

---

## ✅ Production Checklist

### Before Go-Live

- [ ] All services healthy
- [ ] SSL certificates valid
- [ ] DNS configured correctly
- [ ] Monitoring dashboards accessible
- [ ] Backups configured and tested
- [ ] Error tracking (Sentry) enabled
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation reviewed
- [ ] Team trained on operations

### Launch Day

- [ ] Monitor dashboards continuously
- [ ] Watch error logs
- [ ] Track response times
- [ ] Monitor resource usage
- [ ] Have rollback plan ready
- [ ] Backup created before launch

### Post-Launch

- [ ] Monitor for 24 hours
- [ ] Review performance metrics
- [ ] Check error rates
- [ ] Verify backups running
- [ ] Test all critical features
- [ ] Update documentation with learnings

---

## 🎉 Success!

Your Content Automation Platform is now live in production!

**Quick Links:**
- 🌐 Main App: https://yourdomain.com
- 📚 API Docs: https://yourdomain.com/docs
- 📊 Monitoring: https://grafana.yourdomain.com
- 🔄 Status: https://traefik.yourdomain.com

**Next Steps:**
1. Configure OAuth for social platforms
2. Connect your first social media account
3. Create your first content campaign
4. Monitor performance in Grafana
5. Set up alerts for critical metrics

---

**Last Updated:** 2025-12-23
**Platform Version:** 1.0.0-production
**Deployment Status:** ✅ Production-Ready
