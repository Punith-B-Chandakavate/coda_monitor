@echo off
echo =========================================
echo Coda Security Monitor - One-Click Install
echo =========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed!
    echo Please install Docker from: https://docs.docker.com/get-docker/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed!
    echo Please install Docker Compose from: https://docs.docker.com/compose/install/
    exit /b 1
)

echo ✅ Docker and Docker Compose found

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your CODA_API_TOKEN
    echo    Then run: docker-compose up -d
    exit /b 0
)

REM Build and start
echo 🏗️  Building Docker image...
docker-compose build

echo 🚀 Starting Coda Security Monitor...
docker-compose up -d

echo.
echo =========================================
echo ✅ Installation Complete!
echo =========================================
echo 📊 Dashboard: http://localhost:8000
echo 🔧 Admin: http://localhost:8000/admin
echo    Username: admin
echo    Password: admin123
echo.
echo 📝 View logs: docker-compose logs -f
echo 🛑 Stop: docker-compose down
echo =========================================