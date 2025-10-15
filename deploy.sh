# Brain deployment script for Ubuntu server
# Run as: ./deploy.sh

set -e

echo "🚀 Starting Brain deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should NOT be run as root${NC}"
   echo "Run as regular user with docker permissions"
   exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Verify .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}.env file not found${NC}"
    echo "Please create .env file with required variables"
    exit 1
fi

# Verify oracle wallet exists
if [ ! -d app/oracle_wallet ]; then
    echo -e "${RED}Oracle wallet directory not found${NC}"
    echo "Please ensure app/oracle_wallet/ exists with wallet files"
    exit 1
fi

# Create nginx directory if it doesn't exist
mkdir -p nginx

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Remove old images to force rebuild
echo -e "${YELLOW}Cleaning up old images...${NC}"
docker-compose rm -f || true

# Build and start services
echo -e "${YELLOW}Building and starting services...${NC}"
docker-compose up -d --build

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check backend health
echo -e "${YELLOW}Checking backend health...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "Check logs with: docker-compose logs backend"
    exit 1
fi

# Show container status
echo -e "${YELLOW}Container status:${NC}"
docker-compose ps

# Show logs
echo -e "${YELLOW}Recent logs:${NC}"
docker-compose logs --tail=20

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Access the application at:"
echo "  Frontend: http://158.179.212.221"
echo "  API: http://158.179.212.221/api"
echo "  Health: http://158.179.212.221/health"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Restart: docker-compose restart"
echo "  Stop: docker-compose down"
echo "  Status: docker-compose ps"