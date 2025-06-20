# Project-Specific Knowledge Graph Pipeline: Neo4j + Ollama

## Summary

This documentation provides a practical guide to this project's automated knowledge graph pipeline. It details the specific architecture, configuration, and workflows used to transform structured text files (like `gtd.txt`) into a queryable Neo4j graph, powered by a local Ollama LLM. This guide is tailored to the project's codebase and provides an accurate, consolidated overview of its implementation.

---

## Architecture and Setup

The entire application is orchestrated via Docker Compose, ensuring a reproducible and isolated environment. The key services are defined in `docker-compose.yml` and communicate over a dedicated internal network.

### Services

-   **`neo4j`**: The Neo4j database service, which stores the knowledge graph. It is exposed to the host for direct database inspection.
-   **`ollama`**: Runs the Ollama LLM service. It is not exposed to the host machine's ports, communicating exclusively with other services over the internal `app-network`.

### Docker Compose Configuration

The following snippet from `docker-compose.yml` highlights the service setup. Note the use of `app-network` for secure inter-service communication.

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data
    networks:
      - app-network

  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  neo4j_data:
  ollama_data:
```

### Running the System

To start all services in the background, use the following command from the project root:

```bash
docker compose up -d
```

---

## Configuration

The application is configured using environment variables. The `env.example` file provides a template for these variables. When running services that require these variables (like the ingestion script), they must be loaded into the environment.

| Variable          | Description                                           | Default Value                  |
| ----------------- | ----------------------------------------------------- | ------------------------------ |
| `NEO4J_URI`       | The connection URI for the Neo4j database.            | `bolt://localhost:7687`        |
| `NEO4J_USER`      | The username for the Neo4j database.                  | `neo4j`                        |
| `NEO4J_PASSWORD`  | The password for the Neo4j database.                  | `password`                     |
| `LLM_PROVIDER`    | The LLM provider to use (for future expansion).       | `ollama`                       |
| `OLLAMA_BASE_URL` | The base URL for the Ollama API.                      | `http://localhost:11434`       |
| `OLLAMA_MODEL`    | The specific Ollama model to use for generation.      | `qwen3:0.6b`                   |
| `OLLAMA_TIMEOUT`  | The timeout in seconds for requests to the Ollama API. | `120`                          |

*Note: When running scripts from your local machine that connect to services inside Docker, use `localhost` for service addresses. For service-to-service communication within Docker, service names (e.g., `http://ollama:11434`) should be used, but this is handled within the client logic based on environment.*

---

## Core Components

### `Neo4jClient`

All interactions with the Neo4j database are handled by the `Neo4jClient` class in `src/graph/neo4j_client.py`. It uses credentials from environment variables to establish a connection.

**Connection Snippet:**
```python
# src/graph/neo4j_client.py

import os
from neo4j import GraphDatabase

class Neo4jClient:
    """Neo4j client for graph database operations."""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j client.
        """
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = None
        self._connect()
        
    def _connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def ensure_constraints(self):
        """Ensure all necessary constraints are created in the database."""
        # ... (implementation for creating constraints)

### `OllamaLLM` Client

The `OllamaLLM` class in `src/llm/ollama_client.py` manages all communication with the Ollama service. It is responsible for generating text, listing models, and checking the health of the Ollama service.

**Key Methods:**
```python
# src/llm/ollama_client.py

class OllamaLLM(BaseLLM):
    """Ollama LLM client for interacting with local Ollama service."""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 120):
        """
        Initialize Ollama LLM client.
        """
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'qwen3:0.6b')
        self.timeout = timeout
        # ...

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using Ollama model.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = self._make_request('/api/generate', payload)
            if 'response' in response:
                return response['response']
            else:
                raise Exception(f"Invalid response format from Ollama API: {response}")
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Ollama service is healthy.
        """
        try:
            self._make_request('/api/tags', method='GET')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
```

---

## Workflow: Resilient GTD Ingestion with Content Hashing

The primary workflow is the batch ingestion of a structured text file (e.g., `gtd.txt`), managed by the `GraphIngestionService`. This service uses a content-hashing strategy to perform an intelligent, incremental update of the graph, making it highly efficient and resilient to changes.

### Core Principles

1.  **Content as the Source of Truth**: Each note's identity is determined by a SHA256 hash of its content (`content_hash`), not its line number. This hash is stored on the `:GtdNote` node in the graph.
2.  **Uniqueness Guaranteed**: A unique constraint is enforced on the `content_hash` property in Neo4j, ensuring no duplicate notes can exist and making lookups by hash extremely fast.
3.  **Minimal Processing**: The pipeline only ever uses the LLM on notes that are genuinely new. Existing notes are never re-processed, and their positions are updated efficiently.

### Process

1.  **Parse and Hash**: The source text file is parsed into a list of `Note` objects. A unique `content_hash` is generated for each one.
2.  **Compare State**: The service fetches all existing `content_hash` values from the graph and compares them with the hashes from the file. This comparison identifies three distinct sets:
    *   **New Notes**: Hashes present in the file but not the graph.
    -   **Deleted Notes**: Hashes present in the graph but not the file.
    -   **Existing Notes**: Hashes present in both.
3.  **Execute Batched Operations**:
    *   **Add New**: Only the new notes are sent to the LLM for metadata enrichment. They are then added to the graph in a batch `MERGE` operation using their unique hash.
    *   **Update Existing**: A single, efficient Cypher query updates the `line_number` property for all existing notes to reflect any reordering or shifting. No LLM calls are made.
    *   **Remove Deleted**: All notes corresponding to the deleted hashes are removed from the graph using a single `DETACH DELETE` query.
4.  **Rebuild Hierarchy**: Finally, all parent-child (`:HAS_CHILD`) relationships are cleared, and the entire hierarchy is rebuilt from scratch based on the final, correct indentation and line numbers of the notes in the file. This ensures the graph structure always mirrors the document structure.

### LLM Prompt Template

The service uses a specific prompt designed for models like `qwen3` to produce structured JSON.

```
Analyze the following note content and extract structured metadata.
The content is: "{note.content}"
Respond with a JSON object containing:
- "entities": a list of named entities (people, places, concepts).
- "summary": a one-sentence summary of the note.

Example response for "Discuss budget with @john for #project-alpha":
{
  "entities": [
    {"name": "John", "type": "Person"},
    {"name": "Project Alpha", "type": "Project"}
  ],
  "summary": "A task to discuss the budget for Project Alpha with John."
}

Your response must be only the JSON object.
Note content: "{note.content}"
```