import logging
import os
from dotenv import load_dotenv
from src.backend.graph_ingestion_service import GraphIngestionService
from src.graph.neo4j_client import Neo4jClient
from src.llm.factory import get_llm_client

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the GTD file ingestion pipeline.
    """
    logger.info("Starting GTD file ingestion pipeline...")
    # --- Debugging ---
    logger.info(f"LLM Provider from env: {os.getenv('LLM_PROVIDER')}")
    # --- End Debugging ---
    neo4j_client = None
    try:
        # Initialize clients using the factory
        logger.info("Initializing clients...")
        neo4j_client = Neo4jClient()
        llm_client = get_llm_client()

        # Health check for Ollama is now client-specific; can be removed or generalized
        # if hasattr(llm_client, 'health_check') and not llm_client.health_check():
        #     logger.error(f"{llm_client.__class__.__name__} is not healthy.")
        #     return

        # Initialize ingestion service
        ingestion_service = GraphIngestionService(neo4j_client, llm_client)

        # Run ingestion
        gtd_file = "gtd.txt"
        logger.info(f"Ingesting notes from '{gtd_file}'...")
        ingestion_service.ingest_gtd_file(gtd_file)

        logger.info("✅ Ingestion pipeline completed successfully!")
        logger.info("Check your Neo4j browser to see the updated graph.")

    except Exception as e:
        logger.error(f"An error occurred during the ingestion pipeline: {e}", exc_info=True)
    finally:
        if neo4j_client:
            neo4j_client.close()
            logger.info("Neo4j connection closed.")

if __name__ == '__main__':
    main()