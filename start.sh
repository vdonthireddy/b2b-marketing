#!/bin/bash
set -e

echo "Starting JourneyForge..."
docker compose up -d --build

echo ""
echo "JourneyForge is starting up!"
echo "MySQL:      localhost:3306"
echo "Backend:    http://localhost:8000"
echo "Frontend:   http://localhost:3000"
echo ""
echo "Note: The backend will wait for MySQL to be healthy before starting."
echo "You can check the logs with: docker-compose logs -f"
