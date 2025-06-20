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
```

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

## Workflow: Batch GTD Ingestion

The primary workflow is the batch ingestion of a structured text file (e.g., `gtd.txt`), managed by the `GraphIngestionService` in `src/backend/graph_ingestion_service.py`. This service performs a full refresh of the graph, deleting old `:GtdNote` nodes before ingesting new ones to ensure idempotency.

### Process

1.  **Parse File**: The service first parses the structured text file into a list of `Note` objects, preserving indentation to understand hierarchy.
2.  **Enrich with LLM**: For each note, it invokes the `OllamaLLM` client with a specific prompt to extract structured metadata (entities and a summary).
3.  **Ingest to Neo4j**: The enriched data is used to create `:GtdNote` nodes in the Neo4j graph.
4.  **Build Hierarchy**: Finally, it creates `:HAS_CHILD` relationships between the notes based on the original file's indentation, creating a graph that mirrors the document structure.

### LLM Prompt Template

The service uses a specific prompt designed for models like `qwen3` to produce structured JSON.

```
Analyze the following note content and extract structured metadata.
The content is: "{note.content}"
Respond with a JSON object containing:
- "entities": a list of named entities (people, places, concepts).
- "summary": a one-sentence summary of the note.

Example response for "Discuss budget with @john for #project-alpha":
{{
  "entities": ["john", "project-alpha"],
  "summary": "A task to discuss the budget for Project Alpha with John."
}}

Your response must be only the JSON object.
Note content: "{note.content}"
```

### Example Usage

The `GraphIngestionService` can be run as a standalone script for testing, as shown in its `if __name__ == '__main__':` block.

```python
# From src/backend/graph_ingestion_service.py

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create dummy gtd file for testing
    with open("gtd_test.txt", "w") as f:
        f.write("Task 1 #project - Discuss budget with @john for #project-alpha\\n")
        f.write("  Subtask 1.1 - Prepare slides\\n")
        f.write("    Subtask 1.1.1 #detail - Draft initial version\\n")
        f.write("  Subtask 1.2\\n")
        f.write("Task 2 #another - Plan team offsite\\n")

    try:
        neo4j_client = Neo4jClient()
        ollama_client = OllamaLLM()
        
        if not ollama_client.health_check():
            logger.error("Ollama is not running. Please start Ollama to run this script.")
        else:
            ingestion_service = GraphIngestionService(neo4j_client, ollama_client)
            ingestion_service.ingest_gtd_file("gtd_test.txt")
            print("Ingestion successful. Check your Neo4j browser.")
    except Exception as e:
        logger.error(f"An error occurred during ingestion: {e}", exc_info=True)
```

---

## Best Practices

-   **Service Communication**: When running scripts that interact with the Docker services from your local machine, ensure environment variables point to `localhost` (e.g., `http://localhost:11434`). The clients are designed to default to these values.
-   **Health Checks**: Before running intensive processes like ingestion, use the `ollama_client.health_check()` method to ensure the LLM service is available and responsive.
-   **Model Management**: The required Ollama model (e.g., `qwen3:0.6b`) must be pulled before it can be used. You can do this by executing a command inside the running `ollama` container:
    ```bash
    docker compose exec ollama ollama pull qwen3:0.6b
    ```
    To use a different model, update the `OLLAMA_MODEL` environment variable and ensure that model is pulled.
-   **Idempotency**: The ingestion script is designed as a full-refresh mechanism. It clears existing data before adding new notes to ensure the graph is always in sync with the source file.

# Neo4j Management Scripts

## Overview

This project includes two utility scripts for managing the Neo4j database used in the knowledge graph pipeline:

### 1. scripts/clean_neo4j.py
- **Purpose:** Quickly deletes all nodes and relationships from the default Neo4j database.
- **Usage:**
  ```bash
  python scripts/clean_neo4j.py
  ```
- **Behavior:**
  - Connects to the Neo4j instance using default credentials (`bolt://localhost:7687`, user: `neo4j`, password: `password`).
  - Reports the number of nodes and relationships before and after cleaning.
  - Verifies that the database is empty after the operation.

### 2. scripts/neo4j_database_manager.py
- **Purpose:** Provides a more comprehensive management interface for Neo4j.
- **Features:**
  - Connects to Neo4j and displays database information (name, version, edition, node/label counts).
  - Checks for support of multiple databases and attempts to create a test database (will fail on Community Edition).
  - Allows interactive deletion of all contents, creation of sample data, or both.
- **Usage:**
  ```bash
  python scripts/neo4j_database_manager.py
  ```
  Follow the on-screen prompts to choose the desired operation.

## Neo4j Community Edition Limitations
- **Multiple Databases:**
  - The Community Edition supports only the default `neo4j` and `system` databases.
  - Creating additional named databases is not supported (attempts will result in an error).
- **Recommendation:**
  - For most local and development use cases, the default database is sufficient.
  - If you require multiple databases, consider upgrading to Neo4j Enterprise Edition.

## Credentials
- The scripts use the following default credentials:
  - URI: `bolt://localhost:7687`
  - User: `neo4j`
  - Password: `password`
- Update these values in the scripts if your Neo4j instance uses different credentials.

## Troubleshooting
- Ensure the Neo4j service is running before executing the scripts.
- If you encounter connection errors, verify the URI, username, and password.
- For further details, check the script logs and Neo4j server logs. 