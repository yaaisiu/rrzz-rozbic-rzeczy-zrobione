# Purpose
A local, privacy-first note-taking tool that auto-tags, embeds, and links notes in a Neo4j knowledge graph.

## Functional Requirements
- Capture free-form text notes
- Automatic tagging, extracting and processing, entities & links (LLM)
- Visual graph exploration
- Provider-agnostic LLM (Ollama, OpenAI, Gemini)

## Non-Functional
- Runs fully offline (Docker)
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