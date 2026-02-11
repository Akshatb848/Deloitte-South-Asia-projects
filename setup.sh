#!/bin/bash

# Education Intelligence Dashboard - Setup Script
# Ministry of Education, Government of India
# Technology Partner: Deloitte Touche Tohmatsu

set -e

echo "======================================================================="
echo "Education Intelligence Dashboard - Setup"
echo "Ministry of Education, Government of India"
echo "======================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

echo ""

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your configuration${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs vector_db config
echo -e "${GREEN}✓ Directories created${NC}"

echo ""

# Build and start services
echo "Building Docker images..."
docker-compose build

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check backend health
echo "Checking backend health..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Waiting for backend... (attempt $RETRY_COUNT/$MAX_RETRIES)"
        sleep 3
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${YELLOW}⚠ Backend health check timed out${NC}"
fi

echo ""

# Pull LLM model
echo "Pulling LLM model (Mistral 7B Instruct)..."
echo "This may take several minutes depending on your internet connection..."
docker exec education-dashboard-ollama ollama pull mistral:7b-instruct

echo ""
echo "======================================================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "======================================================================="
echo ""
echo "Access points:"
echo "  • Dashboard: http://localhost:8080"
echo "  • API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:8080 in your browser"
echo "  2. Explore the calendar timeline and select different months"
echo "  3. Click the chat button to interact with the AI assistant"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "======================================================================="
