#!/bin/sh
# This script waits for Ollama to be available and then pulls the specified model.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-"http://localhost:11434"}
OLLAMA_MODEL=${OLLAMA_MODEL:-"qwen3:0.6b"}

echo "Ollama Pull Script Started"
echo "Ollama URL: $OLLAMA_BASE_URL"
echo "Ollama Model: $OLLAMA_MODEL"

# --- Wait for Ollama to be Ready ---
echo "Waiting for Ollama to become available..."
# Use a simple loop with curl to check for availability
until curl -s -f -o /dev/null "$OLLAMA_BASE_URL"
do
  echo "Ollama not yet available, sleeping for 5 seconds..."
  sleep 5
done
echo "Ollama is available."

# --- Pull the Model ---
echo "Pulling model: $OLLAMA_MODEL"
# Use curl to send a POST request to the /api/pull endpoint
curl "$OLLAMA_BASE_URL/api/pull" -d "{\"name\": \"$OLLAMA_MODEL\"}"

echo "Model pull command sent. The model will now download in the background."
echo "Ollama Pull Script Finished" 