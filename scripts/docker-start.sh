#!/bin/bash

# Docker startup script for the project
# This script starts all services and ensures they're properly initialized

set -e

echo "🚀 Starting rrzz-rozbic-rzeczy-zrobione services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."

# Wait for Neo4j
echo "Waiting for Neo4j..."
until docker-compose exec -T neo4j cypher-shell -u neo4j -p password "RETURN 1;" > /dev/null 2>&1; do
    echo "Neo4j not ready yet..."
    sleep 5
done
echo "✅ Neo4j is ready!"

# Wait for Ollama
echo "Waiting for Ollama..."
until curl -f http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Ollama not ready yet..."
    sleep 5
done
echo "✅ Ollama is ready!"

# Wait for FastAPI backend
echo "Waiting for FastAPI backend..."
until curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "Backend not ready yet..."
    sleep 5
done
echo "✅ Backend is ready!"

echo "🎉 All services are running!"
echo ""
echo "📋 Service URLs:"
echo "  - FastAPI Backend: http://localhost:8000"
echo "  - Neo4j Browser: http://localhost:7474"
echo "  - Streamlit Frontend: http://localhost:8501"
echo "  - Ollama API: http://localhost:11434"
echo ""
echo "📚 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart" 