#!/usr/bin/env bash
set -euo pipefail

# India Knowledge Graph — Production Deployment & Health Probe Script

echo "=========================================================="
echo "    India Knowledge Graph (IKG) Deployment Engine"
echo "=========================================================="

ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️ Warning: .env file not found. Generating default from configuration..."
fi

echo "1. Checking Docker and Docker Compose..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH."
    exit 1
fi

echo "2. Validating Docker Compose configuration..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml config --quiet
echo "✓ Docker Compose configuration is valid."

echo "3. Building & Starting Services in background..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "4. Awaiting Database and Backend health..."
for i in {1..30}; do
    if curl -s -f http://localhost:8000/api/v1/health > /dev/null; then
        echo "✓ Backend API is healthy and accepting requests."
        break
    fi
    echo "Waiting for services to become healthy... ($i/30)"
    sleep 2
done

echo "5. Running Database Migrations..."
docker compose exec -T backend alembic upgrade head

echo "=========================================================="
echo "🎉 India Knowledge Graph is LIVE!"
echo "   - Frontend UI: http://localhost"
echo "   - Backend API: http://localhost:8000 (or http://localhost/api/v1)"
echo "   - Swagger Docs: http://localhost/docs"
echo "   - Health & Metrics: http://localhost:8000/api/v1/metrics"
echo "=========================================================="
