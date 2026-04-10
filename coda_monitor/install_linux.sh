#!/bin/bash

echo "========================================="
echo "Coda Security Monitor - One-Click Install"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env .env
    echo "⚠️  Please edit .env file and add your CODA_API_TOKEN"
    echo "   Then run: docker-compose up -d"
    exit 0
fi

# Check if CODA_API_TOKEN is set
source .env
if [ -z "$CODA_API_TOKEN" ] || [ "$CODA_API_TOKEN" = "your_coda_api_token_here" ]; then
    echo "⚠️  Please set your CODA_API_TOKEN in .env file"
    echo "   Then run: docker-compose up -d"
    exit 0
fi

# Build and start
echo "🏗️  Building Docker image..."
docker-compose build

echo "🚀 Starting Coda Security Monitor..."
docker-compose up -d

# Wait for container to be ready
echo "⏳ Waiting for service to start..."
sleep 10


echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo "📊 Dashboard: http://localhost:8000"
echo "🔧 Admin: http://localhost:8000/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 View logs: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
echo "========================================="