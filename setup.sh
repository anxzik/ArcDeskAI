#!/bin/bash

echo "Starting ArcDeskAI setup..."

# Build and start the docker containers
docker compose up -d --build

# Wait for the database to be ready
echo "Waiting for database to start..."
sleep 10

# Run database migrations
docker compose exec backend alembic upgrade head

echo "ArcDeskAI setup complete!"
echo "Frontend is running on http://localhost:3000"
echo "Backend is running on http://localhost:8000"