#!/bin/bash

# Startup script for Ollama service
# This script ensures the default model is available and the service is healthy

set -e

echo "Starting Ollama service..."

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until curl -f http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "Ollama not ready yet, waiting..."
    sleep 5
done

echo "Ollama is ready!"

# Check if default model is available
echo "Checking for default model: qwen3:0.6b"
if ! ollama list | grep -q "qwen3:0.6b"; then
    echo "Pulling default model: qwen3:0.6b"
    ollama pull qwen3:0.6b
else
    echo "Default model qwen3:0.6b is already available"
fi

# Test the model
echo "Testing default model..."
if ollama run qwen3:0.6b "Hello, this is a test message." > /dev/null 2>&1; then
    echo "✅ Default model test successful"
else
    echo "❌ Default model test failed"
fi

echo "Ollama startup complete!"
echo "Available models:"
ollama list

# Keep the container running
tail -f /dev/null 