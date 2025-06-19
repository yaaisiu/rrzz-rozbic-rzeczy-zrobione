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