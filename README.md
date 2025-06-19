# rrzz-rozbic-rzeczy-zrobione

## Purpose
A local, privacy-first note-taking tool that auto-tags, embeds, and links notes in a Neo4j knowledge graph.

## Functional Requirements
- Capture free-form text notes
- Automatic tagging, entities & links (LLM)
- Visual graph exploration
- Provider-agnostic LLM (Ollama, OpenAI, Gemini)

## Non-Functional
- Runs fully offline (Docker)
- <500 ms query latency for up to 10k notes
- ≤4 GB RAM baseline

## Tech Stack
- UI: Streamlit
- API: FastAPI
- LLM: Ollama (default) via OpenAI-compatible endpoint
- Graph DB: Neo4j 5.x
- DevEnv: VS Code + Cursor in Dev Container

## Current Status ✅

**Backend Implementation Complete!** The core note ingestion pipeline is fully functional:

- ✅ **LLM Integration**: Ollama with qwen3:0.6b model (optimized for memory constraints)
- ✅ **Note Processing**: Automatic tag extraction, entity recognition, and highlighting
- ✅ **Graph Storage**: Neo4j integration with proper node/relationship management
- ✅ **API Layer**: Complete FastAPI backend with RESTful endpoints
- ✅ **Error Handling**: Robust error handling and logging throughout
- ✅ **Performance**: Clean responses with `think: false` for faster processing

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for containers

### 1. Clone and Setup
```bash
git clone <repository-url>
cd rrzz-rozbic-rzeczy-zrobione
cp env.example .env
```

### 2. Start All Services
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start all services (FastAPI, Neo4j, Ollama, Streamlit)
./scripts/docker-start.sh
```

### 3. Access Services
- **FastAPI Backend**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password)
- **Streamlit Frontend**: http://localhost:8501
- **Ollama API**: http://localhost:11434

### 4. Test the Pipeline
```bash
# Test the complete ingestion pipeline
python test_ingestion_quick.py

# Test individual components
python examples/test_ollama.py
```

### 5. Use the API
```bash
# Ingest a note via API
curl -X POST http://localhost:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"content": "I need to finish the Python project by Friday."}'

# Search notes
curl -X POST http://localhost:8000/notes/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python project"}'
```

### Service Management
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

## API Endpoints

The FastAPI backend provides the following endpoints:

- `POST /notes` - Ingest a single note
- `POST /notes/batch` - Ingest multiple notes in batch
- `GET /notes/{note_id}` - Retrieve a specific note
- `POST /notes/search` - Search notes by content or tags
- `GET /notes` - List recent notes
- `GET /health` - Health check with service status

## Development Setup (Alternative)
1. Clone the repo
2. Build and start the dev container in VS Code (with Cursor)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in required values
5. Run services with Docker Compose
6. Access FastAPI at `localhost:8000`, Streamlit at `localhost:8501`, Neo4j at `localhost:7474`, and Ollama at `localhost:11434`

## Key Features Implemented

### LLM Integration
- **Model**: qwen3:0.6b (optimized for memory constraints)
- **Features**: Automatic tag extraction, entity recognition, highlighting
- **Performance**: Clean responses with `think: false` for faster processing
- **Fallback**: Graceful error handling when LLM processing fails

### Graph Database
- **Storage**: Neo4j with proper node and relationship management
- **Schema**: Notes, Tags, Entities with appropriate relationships
- **Search**: Full-text search across notes and tags
- **Upsert**: Prevents duplicate notes and maintains data integrity

### API Layer
- **RESTful**: Complete CRUD operations for notes
- **Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error responses and logging
- **Health Checks**: Service status monitoring

## Next Steps

### Immediate Priorities
1. **Frontend Development**: Implement Streamlit interface for note input and visualization
2. **Graph Visualization**: Add Neo4j Bloom integration for graph exploration
3. **Embedding Implementation**: Replace placeholder embeddings with actual vector generation
4. **Performance Optimization**: Implement caching and batch processing

### Future Enhancements
- **Multi-provider LLM**: Support for OpenAI, Gemini, and other providers
- **Advanced Search**: Semantic search with embeddings
- **Sync & Backup**: Automated backup and synchronization features
- **Mobile Interface**: Responsive design for mobile devices

## Jupyter Notebooks

The `notebooks/`