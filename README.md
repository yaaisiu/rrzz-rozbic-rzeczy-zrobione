# rrzz-rozbic-rzeczy-zrobione

A local, privacy-first note-taking tool that auto-tags, embeds, and links notes from a text file into a Neo4j knowledge graph.

## Tech Stack
- **CLI**: Python
- **LLM**: Ollama (default)
- **Graph DB**: Neo4j 5.x
- **Containerization**: Docker, Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose installed

### 1. Clone and Setup
```bash
git clone <repository-url>
cd rrzz-rozbic-rzeczy-zrobione
```

### 2. Start Docker Services
You have two options to start the services:

#### Option A: Using the startup script (Recommended)
```bash
# Make the script executable
chmod +x scripts/docker-start.sh

# Start all services
./scripts/docker-start.sh
```

#### Option B: Manual Docker Compose
```bash
# Start services in detached mode
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Pull LLM Model (Optional)
After services are running, you can pull a specific model for Ollama:

```bash
# Make the script executable
chmod +x scripts/pull_model.sh

# Pull default model (qwen3:0.6b)
./scripts/pull_model.sh

# Or pull a specific model
OLLAMA_MODEL=llama3.2:3b ./scripts/pull_model.sh
```

### 4. Verify Services
Once everything is running, you can access:

- **Neo4j Browser**: http://localhost:7474
  - Username: `neo4j`
  - Password: `password`
- **Ollama API**: http://localhost:11434

### 5. Useful Commands

```bash
# View service logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Check service status
docker-compose ps

# Access Neo4j shell
docker-compose exec neo4j cypher-shell -u neo4j -p password

# Access Ollama container
docker-compose exec ollama ollama list
```

### 6. Environment Setup
Copy the example environment file and configure as needed:
```bash
cp env.example .env
# Edit .env with your specific configurations
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_graph.py
python -m pytest tests/test_llm.py
python -m pytest tests/test_ingestion.py
```

### Project Structure
```
src/
├── backend/          # Backend services
├── graph/           # Neo4j graph operations
├── llm/             # LLM client implementations
└── utils/           # Utility functions

config/              # Configuration files
scripts/             # Docker and setup scripts
tests/               # Test files
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 7474 or 7687 are in use, modify `docker-compose.yml`
2. **Ollama model not found**: Run the pull model script or manually pull via `docker-compose exec ollama ollama pull <model>`
3. **Neo4j connection issues**: Wait for the service to fully initialize (can take 30-60 seconds)

### Service Health Checks
```bash
# Check Neo4j
curl http://localhost:7474

# Check Ollama
curl http://localhost:11434/api/tags
```

## Environment Variables

To configure the application, create a `.env` file in the root directory by copying the `env.example` file:

*   `google`: Uses the Google Gemini API. Requires `GOOGLE_API_KEY` to be set in the environment.
*   `openai`: Uses the OpenAI API. Requires `OPENAI_API_KEY` to be set in the environment.