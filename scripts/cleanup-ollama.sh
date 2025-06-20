#!/bin/bash

# Ollama cleanup script
# This script properly stops and removes Ollama containers and cleans up related resources

set -e

echo "🧹 Starting Ollama cleanup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Find and stop any running Ollama containers
echo "🔍 Looking for Ollama containers..."
OLLAMA_CONTAINERS=$(docker ps -q --filter "name=ollama" 2>/dev/null || true)

if [ -n "$OLLAMA_CONTAINERS" ]; then
    echo "🛑 Found running Ollama containers, stopping them..."
    echo "$OLLAMA_CONTAINERS" | xargs -r docker stop
    echo "✅ Ollama containers stopped"
else
    echo "ℹ️  No running Ollama containers found"
fi

# Find and remove any stopped Ollama containers
echo "🗑️  Looking for stopped Ollama containers..."
STOPPED_OLLAMA_CONTAINERS=$(docker ps -aq --filter "name=ollama" 2>/dev/null || true)

if [ -n "$STOPPED_OLLAMA_CONTAINERS" ]; then
    echo "🗑️  Removing stopped Ollama containers..."
    echo "$STOPPED_OLLAMA_CONTAINERS" | xargs -r docker rm
    echo "✅ Ollama containers removed"
else
    echo "ℹ️  No stopped Ollama containers found"
fi

# Remove Ollama-related networks if they exist and are not in use
echo "🌐 Checking for Ollama-related networks..."
OLLAMA_NETWORKS=$(docker network ls --filter "name=ollama" --format "{{.Name}}" 2>/dev/null || true)

if [ -n "$OLLAMA_NETWORKS" ]; then
    echo "🗑️  Removing Ollama-related networks..."
    echo "$OLLAMA_NETWORKS" | while read network; do
        if docker network rm "$network" 2>/dev/null; then
            echo "✅ Removed network: $network"
        else
            echo "⚠️  Could not remove network: $network (may be in use)"
        fi
    done
else
    echo "ℹ️  No Ollama-related networks found"
fi

# Check for app-network that might be used by Ollama
echo "🌐 Checking for app-network..."
if docker network ls | grep -q "app-network"; then
    APP_NETWORK=$(docker network ls --filter "name=app-network" --format "{{.Name}}" | head -1)
    if [ -n "$APP_NETWORK" ]; then
        echo "🗑️  Attempting to remove app-network: $APP_NETWORK"
        if docker network rm "$APP_NETWORK" 2>/dev/null; then
            echo "✅ Removed app-network: $APP_NETWORK"
        else
            echo "⚠️  Could not remove app-network: $APP_NETWORK (may be in use by other services)"
        fi
    fi
else
    echo "ℹ️  No app-network found"
fi

# Optional: Remove Ollama image (uncomment if you want to free up more space)
# echo "🗑️  Removing Ollama image..."
# if docker rmi ollama/ollama 2>/dev/null; then
#     echo "✅ Ollama image removed"
# else
#     echo "ℹ️  Ollama image not found or could not be removed"
# fi

# Optional: Remove Ollama volumes (uncomment if you want to free up more space)
# echo "🗑️  Removing Ollama volumes..."
# OLLAMA_VOLUMES=$(docker volume ls --filter "name=ollama" --format "{{.Name}}" 2>/dev/null || true)
# if [ -n "$OLLAMA_VOLUMES" ]; then
#     echo "$OLLAMA_VOLUMES" | xargs -r docker volume rm
#     echo "✅ Ollama volumes removed"
# else
#     echo "ℹ️  No Ollama volumes found"
# fi

echo "🎉 Ollama cleanup completed!"
echo ""
echo "📋 Summary:"
echo "  - Stopped and removed Ollama containers"
echo "  - Cleaned up Ollama-related networks"
echo "  - Space saved: Ollama containers and networks removed"
echo ""
echo "💡 To start Ollama again, use: docker-compose --profile ollama up -d" 