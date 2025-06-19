# Data Flow

1.  **User Input**: User edits the `gtd.txt` file.
2.  **CLI Execution**: The user runs the `run_ingestion.py` script.
3.  **File Parsing**: The script reads and parses the `gtd.txt` file.
4.  **LLM Processing**: The script sends notes to an LLM (Ollama) to extract tags, entities, and other metadata.
5.  **Graph Ingestion**: The processed notes and metadata are ingested into Neo4j.
6.  **Graph Exploration**: The user explores the knowledge graph visually using the Neo4j Browser.