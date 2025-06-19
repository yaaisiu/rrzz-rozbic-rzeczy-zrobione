import streamlit as st
import os
import logging

from src.backend.graph_ingestion_service import GraphIngestionService
from src.graph.neo4j_client import Neo4jClient
from src.llm.ollama_client import OllamaLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
GTD_FILE_PATH = "gtd.txt"

# --- Page Setup ---
st.set_page_config(
    page_title="GTD Note Editor",
    page_icon="📝",
    layout="wide",
)

st.title("📝 GTD Note Editor")
st.markdown("Edit your notes below. Click 'Save & Update Graph' to persist changes and sync with Neo4j.")

# --- Functions ---
def load_file_content(file_path: str) -> str:
    """Loads content from a file. Creates it if it doesn't exist."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("# Welcome to your GTD file!\n- Start adding your tasks here.\n")
    with open(file_path, 'r') as f:
        return f.read()

def save_file_content(file_path: str, content: str):
    """Saves content to a file."""
    with open(file_path, 'w') as f:
        f.write(content)
    logger.info(f"Successfully saved content to {file_path}")

def update_graph(file_path: str):
    """Triggers the graph ingestion service to update Neo4j."""
    neo4j_client = None
    try:
        st.info("Connecting to Neo4j...")
        neo4j_client = Neo4jClient()
        llm_client = OllamaLLM()
        ingestion_service = GraphIngestionService(neo4j_client, llm_client)
        
        st.info("Updating graph from file...")
        ingestion_service.ingest_gtd_file(file_path)
        
        st.success("✅ Graph updated successfully!")
    except Exception as e:
        logger.error(f"Failed to update graph: {e}", exc_info=True)
        st.error(f"❌ Failed to update graph. See logs for details. Error: {e}")
    finally:
        if neo4j_client:
            neo4j_client.close()
            logger.info("Neo4j connection closed.")

# --- Main Application ---
# Load initial content
initial_content = load_file_content(GTD_FILE_PATH)

# Display the text editor
edited_content = st.text_area(
    label="Your notes file:",
    value=initial_content,
    height=600,
    label_visibility="collapsed"
)

# Save button
if st.button("💾 Save & Update Graph"):
    with st.spinner("Saving file and updating graph..."):
        # 1. Save the file
        save_file_content(GTD_FILE_PATH, edited_content)
        
        # 2. Update the graph
        update_graph(GTD_FILE_PATH)

st.sidebar.info(
    """
    **How it works:**
    1. Edit the text on this page.
    2. Click 'Save & Update Graph'.
    3. The `gtd.txt` file is overwritten.
    4. The app parses the file and updates the Neo4j knowledge graph.
    """
) 