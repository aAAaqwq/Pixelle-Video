#!/bin/bash
# Pixelle-Video Docker Quick Start Script

set -e

echo "🐳 Pixelle-Video Docker Deployment"
echo "=================================="
echo ""

# Check if config.yaml exists
if [ ! -f config.yaml ]; then
    echo "❌ Error: config.yaml not found!"
    echo ""
    echo "Please create config.yaml before starting:"
    echo "  1. Copy from config.example.yaml"
    echo "  2. Fill in your API keys and ComfyUI URL"
    echo ""
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: docker-compose not found!"
    echo ""
    echo "Please install Docker Compose first:"
    echo "  https://docs.docker.com/compose/install/"
    echo ""
    exit 1
fi

# Use docker-compose or docker compose based on availability
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

echo "📦 Building Docker images..."
$DOCKER_COMPOSE build

echo ""
echo "🚀 Starting services..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Pixelle-Video is now running!"
echo ""
echo "Services:"
echo "  🌐 Web UI:  http://localhost:8501"
echo "  🔌 API:     http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Custom Resources (optional):"
echo "  📁 data/bgm/        - Custom background music (overrides default)"
echo "  📁 data/templates/  - Custom HTML templates (overrides default)"
echo "  📁 data/workflows/  - Custom ComfyUI workflows (overrides default)"
echo ""
echo "Useful commands:"
echo "  View logs:    $DOCKER_COMPOSE logs -f"
echo "  Stop:         $DOCKER_COMPOSE down"
echo "  Restart:      $DOCKER_COMPOSE restart"
echo "  Rebuild:      $DOCKER_COMPOSE up -d --build"
echo ""

