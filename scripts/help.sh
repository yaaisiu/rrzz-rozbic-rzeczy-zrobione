#!/bin/bash

# Help script for Docker Compose commands and profiles

echo "🚀 rrzz-rozbic-rzeczy-zrobione - Docker Compose Commands"
echo "=================================================="
echo ""

echo "📋 Basic Commands:"
echo "  docker-compose up -d                    # Start Neo4j only (default)"
echo "  docker-compose --profile ollama up -d   # Start Neo4j + Ollama"
echo "  docker-compose down                     # Stop all services"
echo "  docker-compose ps                       # Show running services"
echo "  docker-compose logs -f                  # Follow logs"
echo ""

echo "🧹 Cleanup Commands:"
echo "  ./scripts/cleanup-ollama.sh             # Clean up Ollama containers/networks"
echo "  docker rmi ollama/ollama                # Remove Ollama image (~1GB)"
echo "  docker volume rm rrzz-rozbic-rzeczy-zrobione_ollama_data  # Remove Ollama data"
echo ""

echo "🔧 Service Access:"
echo "  docker-compose exec neo4j cypher-shell -u neo4j -p password  # Neo4j shell"
echo "  docker-compose exec ollama ollama list                       # List Ollama models"
echo ""

echo "🌐 Service URLs:"
echo "  Neo4j Browser: http://localhost:7474"
echo "  Ollama API: http://localhost:11434"
echo ""

echo "💡 Space Management:"
echo "  Default mode: Only Neo4j runs (saves space)"
echo "  Ollama mode: Both services run (requires ~1GB for image)"
echo "  Cleanup: Remove containers, networks, images, volumes"
echo ""

echo "📚 For more information, see:"
echo "  - README.md"
echo "  - documentation/techstack.md" 