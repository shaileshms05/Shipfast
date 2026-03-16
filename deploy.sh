#!/bin/bash

# ShipFast v3.0 - Production Deployment Script
# Deploys ShipFast to a server using Docker

set -e  # Exit on error

echo "======================================"
echo "ShipFast v3.0 - Production Deployment"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with required variables:"
    echo ""
    echo "CEREBRAS_API_KEY=your_api_key_here"
    echo ""
    exit 1
fi

# Source environment variables
source .env

# Check if CEREBRAS_API_KEY is set
if [ -z "$CEREBRAS_API_KEY" ]; then
    echo -e "${RED}Error: CEREBRAS_API_KEY not set in .env file!${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment variables loaded"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed!${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker Compose is installed"
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p shipfast_output
mkdir -p logs
mkdir -p ssl

echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Stop existing containers
echo "Stopping existing containers (if any)..."
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓${NC} Existing containers stopped"
echo ""

# Build Docker image
echo "Building Docker image..."
docker-compose build --no-cache

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Docker image built successfully"
else
    echo -e "${RED}✗${NC} Docker build failed"
    exit 1
fi
echo ""

# Start containers
echo "Starting ShipFast containers..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Containers started successfully"
else
    echo -e "${RED}✗${NC} Failed to start containers"
    exit 1
fi
echo ""

# Wait for health check
echo "Waiting for application to become healthy..."
sleep 10

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✓${NC} Application is healthy!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${RED}✗${NC} Application failed to become healthy"
        echo ""
        echo "Checking logs..."
        docker-compose logs --tail=50
        exit 1
    fi
    
    echo "Waiting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo ""
echo "======================================"
echo -e "${GREEN}🚀 ShipFast Deployment Complete!${NC}"
echo "======================================"
echo ""
echo "Access points:"
echo "  • Backend API:      http://localhost:8000"
echo "  • API Docs:         http://localhost:8000/docs"
echo "  • Health Check:     http://localhost:8000/health"
echo ""
echo "Nginx (if enabled):"
echo "  • HTTP:             http://localhost:80"
echo "  • HTTPS:            https://localhost:443"
echo ""
echo "Useful commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop:             docker-compose down"
echo "  • Restart:          docker-compose restart"
echo "  • Status:           docker-compose ps"
echo ""
echo "======================================"
