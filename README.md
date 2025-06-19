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

## Milestones
1. Scaffold & containerize (today)
2. Note ingestion & tagging (today)
3. Graph explorer (today)
4. Sync & backup jobs (T+2 days)

## Setup Instructions
1. Clone the repo
2. Build and start the dev container in VS Code (with Cursor)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in required values
5. Run services with Docker Compose
6. Access FastAPI at `localhost:8000`, Streamlit at `localhost:8501`, Neo4j at `localhost:7474`, and Ollama at `localhost:11434`

## Jupyter Notebooks

The `notebooks/` directory contains interactive Jupyter notebooks for development, testing, and analysis:

### 📝 `prompt_testing.ipynb` - Prompt Development & Testing
**Purpose**: Test and refine LLM prompts for note processing tasks.

**Features**:
- Pre-built prompts for tagging, entity extraction, and relationship identification
- Sample notes with realistic content for testing
- Functions to test prompts across different LLM providers
- Prompt optimization and comparison tools

**Use Cases**:
- Develop effective prompts before production deployment
- Compare prompt performance across different models
- Fine-tune prompts for specific note types or domains

### ⚖️ `llm_provider_comparison.ipynb` - LLM Provider Benchmarking
**Purpose**: Compare performance and quality across Ollama, OpenAI, and Gemini providers.

**Features**:
- Automated benchmarking for response time and quality
- Standardized test prompts for fair comparison
- Cost analysis and performance metrics
- Provider-specific configuration testing

**Use Cases**:
- Choose the optimal LLM provider for your use case
- Balance cost, speed, and quality requirements
- Test provider reliability and consistency

### 🕸️ `graph_analysis.ipynb` - Neo4j Graph Exploration
**Purpose**: Analyze and visualize your knowledge graph structure.

**Features**:
- Pre-built Cypher queries for graph statistics
- Node and relationship analysis
- Identification of orphaned notes and popular tags
- Graph connectivity and clustering analysis

**Use Cases**:
- Understand knowledge graph structure and growth
- Find insights and patterns in your notes
- Identify areas for better note organization
- Monitor graph health and connectivity

### 🔄 `data_pipeline_testing.ipynb` - End-to-End Pipeline Testing
**Purpose**: Test the complete data flow from note input to graph storage.

**Features**:
- API endpoint testing and validation
- Pipeline component integration testing
- End-to-end workflow verification
- Performance monitoring and bottleneck identification

**Use Cases**:
- Ensure pipeline reliability and correctness
- Debug integration issues between components
- Validate data transformations and storage
- Monitor pipeline performance under load

### 🔍 `embedding_analysis.ipynb` - Semantic Similarity & Clustering
**Purpose**: Work with embeddings for semantic search and note clustering.

**Features**:
- Embedding generation and comparison
- Cosine similarity calculations between notes
- Note clustering and topic identification
- Semantic search functionality testing

**Use Cases**:
- Improve search relevance and accuracy
- Discover hidden connections between notes
- Identify note clusters and topics
- Optimize embedding models for your content

### Getting Started with Notebooks

1. **Install Jupyter dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Jupyter**:
   ```bash
   jupyter notebook notebooks/
   # or
   jupyter lab notebooks/
   ```

3. **Configure environment**:
   - Ensure your `.env` file contains required API keys
   - Start necessary services (Neo4j, FastAPI, Ollama)
   - Update notebook configurations as needed

4. **Run notebooks**:
   - Start with `prompt_testing.ipynb` to develop your prompts
   - Use `llm_provider_comparison.ipynb` to choose your provider
   - Test your pipeline with `data_pipeline_testing.ipynb`
   - Analyze results with `graph_analysis.ipynb` and `embedding_analysis.ipynb`

### Notebook Dependencies

The notebooks require additional Python packages for data analysis and visualization:
- `pandas`, `numpy` - Data manipulation and analysis
- `matplotlib`, `seaborn` - Data visualization
- `scikit-learn` - Machine learning and clustering
- `networkx` - Graph analysis
- `requests` - API testing

All dependencies are included in `requirements.txt`. 