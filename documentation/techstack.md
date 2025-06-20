# Tech Stack

- **CLI**: Python
- **LLM**: Ollama (optional via Docker Compose profiles), with support for other providers
- **Graph Database**: Neo4j 5.x
- **Containerization**: Docker, Docker Compose with profiles
- **Development Environment**: VS Code + Cursor, Dev Containers

## Docker Compose Profiles

The system uses Docker Compose profiles to manage optional services:

### Default Profile (Neo4j only)
```bash
docker-compose up -d
```
Starts only Neo4j database service.

### Ollama Profile (Neo4j + Ollama)
```bash
docker-compose --profile ollama up -d
```
Starts both Neo4j and Ollama services. Ollama image will be downloaded on first run.

### Cleanup
```bash
# Stop all services
docker-compose down

# Clean up Ollama containers and networks (if needed)
./scripts/cleanup-ollama.sh
```

## Space Management

- **Default mode**: Only Neo4j runs, saving space when Ollama is not needed
- **Ollama mode**: Both services run, with Ollama image (~1GB) downloaded
- **Cleanup script**: Removes Ollama containers, networks, and optionally images/volumes for maximum space savings