#!/bin/bash

echo "========================================="
echo "Coda Security Monitor - One-Click Install"
echo "========================================="

# Detect OS
OS="$(uname -s)"

install_docker_linux() {
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh

    echo "Adding current user to docker group..."
    sudo usermod -aG docker $USER

    echo "Restarting Docker..."
    sudo systemctl start docker
}

install_compose_linux() {
    echo "Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
}

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"

    if [[ "$OS" == "Linux" ]]; then
        install_docker_linux
    else
        echo "⚠️ Please install Docker Desktop manually:"
        echo "👉 https://docs.docker.com/get-docker/"
        exit 1
    fi
else
    echo "✅ Docker found"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found"

    if [[ "$OS" == "Linux" ]]; then
        install_compose_linux
    else
        echo "⚠️ Please install Docker Compose via Docker Desktop"
        exit 1
    fi
else
    echo "✅ Docker Compose found"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env .env 2>/dev/null || touch .env
    echo "⚠️  Please edit .env and add CODA_API_TOKEN"
    exit 0
fi

# Load env
source .env

if [ -z "$CODA_API_TOKEN" ] || [ "$CODA_API_TOKEN" = "your_coda_api_token_here" ]; then
    echo "⚠️ Please set CODA_API_TOKEN in .env"
    exit 0
fi

# Build & run
echo "🏗️ Building Docker image..."
docker-compose build

echo "🚀 Starting service..."
docker-compose up -d

echo "⏳ Waiting for startup..."
sleep 10

echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo "📊 Dashboard: http://localhost:8000"
echo "🔧 Admin: http://localhost:8000/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo "========================================="