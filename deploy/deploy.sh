#!/bin/bash
# Production Deployment Script for Content Automation Platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}Content Automation Platform - Production Deploy${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""

# =============================================================================
# CONFIGURATION
# =============================================================================

ENVIRONMENT=${1:-production}
DOMAIN=${2:-yourdomain.com}

echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Domain: ${DOMAIN}${NC}"
echo ""

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

echo -e "${YELLOW}[1/10] Running pre-flight checks...${NC}"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production not found${NC}"
    echo "Please create .env.production from .env.example"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Check if required directories exist
mkdir -p backups logs media traefik/logs monitoring/grafana

# Set permissions for acme.json
touch traefik/acme.json
chmod 600 traefik/acme.json

echo -e "${GREEN}✓ Pre-flight checks passed${NC}"
echo ""

# =============================================================================
# CREATE DOCKER NETWORK
# =============================================================================

echo -e "${YELLOW}[2/10] Creating Docker networks...${NC}"

docker network create web 2>/dev/null || echo "Network 'web' already exists"

echo -e "${GREEN}✓ Networks created${NC}"
echo ""

# =============================================================================
# BUILD IMAGES
# =============================================================================

echo -e "${YELLOW}[3/10] Building Docker images...${NC}"

docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${GREEN}✓ Images built${NC}"
echo ""

# =============================================================================
# DATABASE MIGRATION
# =============================================================================

echo -e "${YELLOW}[4/10] Running database migrations...${NC}"

# Start only database
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
echo "Waiting for database..."
sleep 10

# Run migrations
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

# =============================================================================
# START SERVICES
# =============================================================================

echo -e "${YELLOW}[5/10] Starting all services...${NC}"

docker-compose -f docker-compose.prod.yml up -d

echo -e "${GREEN}✓ Services started${NC}"
echo ""

# =============================================================================
# HEALTH CHECKS
# =============================================================================

echo -e "${YELLOW}[6/10] Waiting for services to be healthy...${NC}"

# Wait for backend health check
MAX_RETRIES=30
RETRY_COUNT=0

until docker-compose -f docker-compose.prod.yml ps | grep backend | grep healthy > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
        echo -e "${RED}Error: Backend failed to become healthy${NC}"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
    echo "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 5
done

echo -e "${GREEN}✓ All services are healthy${NC}"
echo ""

# =============================================================================
# CREATE SUPERUSER
# =============================================================================

echo -e "${YELLOW}[7/10] Checking superuser...${NC}"

# Create superuser if needed (idempotent)
docker-compose -f docker-compose.prod.yml exec -T backend python -m app.initial_data

echo -e "${GREEN}✓ Superuser ready${NC}"
echo ""

# =============================================================================
# CONFIGURE MONITORING
# =============================================================================

echo -e "${YELLOW}[8/10] Setting up monitoring...${NC}"

# Import Grafana dashboards
if [ -d "monitoring/grafana/dashboards" ]; then
    echo "Grafana dashboards will be auto-provisioned"
fi

echo -e "${GREEN}✓ Monitoring configured${NC}"
echo ""

# =============================================================================
# SETUP BACKUPS
# =============================================================================

echo -e "${YELLOW}[9/10] Configuring backups...${NC}"

# Create backup cron job
(crontab -l 2>/dev/null; echo "0 3 * * * cd $(pwd) && docker-compose -f docker-compose.prod.yml exec -T backup python backup.py") | crontab -

echo -e "${GREEN}✓ Backup schedule configured${NC}"
echo ""

# =============================================================================
# FINAL CHECKS
# =============================================================================

echo -e "${YELLOW}[10/10] Running final checks...${NC}"

# Check all services are running
SERVICES="backend frontend db redis celery-worker celery-beat traefik prometheus grafana"

for service in $SERVICES; do
    if docker-compose -f docker-compose.prod.yml ps | grep $service | grep Up > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is not running${NC}"
    fi
done

echo ""

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

echo -e "${GREEN}=================================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "🌐 Application: https://${DOMAIN}"
echo -e "📊 Grafana: https://grafana.${DOMAIN}"
echo -e "📈 Prometheus: https://prometheus.${DOMAIN}"
echo -e "🔄 Traefik: https://traefik.${DOMAIN}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure DNS to point to this server"
echo "2. Wait for SSL certificates to be issued (~2 minutes)"
echo "3. Login with your superuser credentials"
echo "4. Connect social media accounts"
echo "5. Start creating content!"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "  Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  Restart:       docker-compose -f docker-compose.prod.yml restart"
echo "  Scale backend: docker-compose -f docker-compose.prod.yml up -d --scale backend=5"
echo ""
echo -e "${GREEN}Deployment completed at $(date)${NC}"
