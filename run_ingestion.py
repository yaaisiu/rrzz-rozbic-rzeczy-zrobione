import logging
from src.backend.graph_ingestion_service import GraphIngestionService
from src.graph.neo4j_client import Neo4jClient
from src.llm.ollama_client import OllamaLLM

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the GTD file ingestion pipeline.
    """
    logger.info("Starting GTD file ingestion pipeline...")
    neo4j_client = None
    try:
        # Initialize clients
        logger.info("Initializing clients...")
        neo4j_client = Neo4jClient()
        ollama_client = OllamaLLM()

        # Health check for Ollama
        logger.info("Checking Ollama service health...")
        if not ollama_client.health_check():
            logger.error("Ollama is not running. Please start Ollama to run this script.")
            return

        logger.info("Ollama service is healthy.")

        # Initialize ingestion service
        ingestion_service = GraphIngestionService(neo4j_client, ollama_client)

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