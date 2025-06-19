# Data Flow

1. **User Input**: User enters a notes via Streamlit UI. He will use it as regular notepad text editor.
2. **API Ingestion**: Note is sent to FastAPI backend via POST /notes. NOTE: We want to process them in the background somehow, after some time of inactivity, or button press for a starter solution.
3. **LLM Processing**: Backend uses LLM (Ollama/OpenAI/Gemini) to tag, extract entities, and generate embeddings.
4. **Graph Storage**: Processed note, tags, and embeddings are upserted into Neo4j (using LangChain Neo4jVector). NOTE: Of course they need to be checked against each other, so we don't multiply beings. Simple system for the beginning.
5. **Graph Exploration**: User explores notes and relationships visually via Streamlit and Neo4j Bloom/Browser. 