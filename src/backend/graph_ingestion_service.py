import logging
import json
import re
from typing import List, Dict, Any

from src.backend.file_parser import parse_file, Note
from src.graph.neo4j_client import Neo4jClient
from src.llm.ollama_client import OllamaLLM

logger = logging.getLogger(__name__)

class GraphIngestionService:
    def __init__(self, neo4j_client: Neo4jClient, llm_client: OllamaLLM):
        self.client = neo4j_client
        self.llm_client = llm_client

    def clear_gtd_notes(self):
        """Removes all GtdNote nodes and their relationships from the graph."""
        logger.info("Clearing all GtdNote nodes from the graph.")
        query = "MATCH (n:GtdNote) DETACH DELETE n"
        self.client.execute_query(query)
        logger.info("Successfully cleared GtdNote nodes.")

    def ingest_notes(self, notes: List[Note]) -> List[str]:
        """
        Ingests a list of notes into the graph, creating a GtdNote node for each.
        It uses an LLM to extract metadata for each note.
        Returns a list of the created node IDs.
        """
        node_ids: List[str] = []
        logger.info(f"Starting ingestion for {len(notes)} notes...")
        for i, note in enumerate(notes):
            logger.info(f"[{i+1}/{len(notes)}] Processing note on line {note.line_number}: '{note.content[:70]}...'")

            # 1. Get LLM metadata
            prompt = f"""
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
            """
            llm_response_str = self.llm_client.generate(prompt)
            
            # 2. Parse LLM response
            try:
                # Use regex to find the JSON block, even if it's wrapped in markdown
                json_match = re.search(r'\{.*\}', llm_response_str, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    llm_metadata = json.loads(json_str)
                else:
                    logger.warning(f"[{i+1}/{len(notes)}] Could not find a JSON object in the LLM response: {llm_response_str}")
                    llm_metadata = {}
            except json.JSONDecodeError:
                logger.warning(f"[{i+1}/{len(notes)}] Failed to parse LLM response as JSON, even after cleaning: {llm_response_str}")
                llm_metadata = {}

            # 3. Flatten the entities from the LLM response
            flat_entities = []
            for entity in llm_metadata.get("entities", []):
                if isinstance(entity, dict) and 'name' in entity:
                    entity_type = entity.get('type', 'entity')
                    flat_entities.append(f"{entity['name']} ({entity_type})")
                elif isinstance(entity, str):
                    flat_entities.append(entity)
            
            logger.info(f"[{i+1}/{len(notes)}] Found entities: {flat_entities}")

            # 4. Create node with enriched data
            query = """
            CREATE (n:GtdNote {
                content: $content,
                line_number: $line_number,
                tags: $tags,
                llm_entities: $llm_entities,
                llm_summary: $llm_summary
            })
            RETURN elementId(n) as node_id
            """
            params = {
                "content": note.content,
                "line_number": note.line_number,
                "tags": note.tags,
                "llm_entities": flat_entities,
                "llm_summary": llm_metadata.get("summary", "")
            }
            result = self.client.execute_query(query, params)
            if result:
                node_ids.append(result[0]['node_id'])
                logger.info(f"[{i+1}/{len(notes)}] Successfully created node in graph.")

        logger.info("Finished ingesting all notes.")
        return node_ids

    def build_hierarchy(self, notes: List[Note], node_ids: List[str]):
        """Builds HAS_CHILD relationships based on indentation."""
        logger.info("Building note hierarchy.")
        note_map = {note.line_number: node_id for note, node_id in zip(notes, node_ids)}
        parent_stack = []  # Stack of (indentation, node_id)

        for note in notes:
            node_id = note_map[note.line_number]
            
            while parent_stack and parent_stack[-1][0] >= note.indentation:
                parent_stack.pop()

            if parent_stack:
                parent_id = parent_stack[-1][1]
                query = """
                MATCH (parent), (child)
                WHERE elementId(parent) = $parent_id AND elementId(child) = $child_id
                CREATE (parent)-[:HAS_CHILD]->(child)
                """
                params = {"parent_id": parent_id, "child_id": node_id}
                self.client.execute_query(query, params)

            parent_stack.append((note.indentation, node_id))
        logger.info("Successfully built note hierarchy.")

    def ingest_gtd_file(self, file_path: str):
        """
        Parses a gtd file and updates the graph.
        This is a full refresh: existing notes are deleted and then recreated.
        """
        logger.info(f"Starting ingestion for file: {file_path}")
        # 1. Parse the file
        notes = parse_file(file_path)

        # 2. Clear existing graph data
        self.clear_gtd_notes()

        # 3. Ingest new notes
        node_ids = self.ingest_notes(notes)

        # 4. Build hierarchy
        if notes and node_ids:
            self.build_hierarchy(notes, node_ids)
        
        logger.info(f"Finished ingestion for file: {file_path}")


if __name__ == '__main__':
    # Example Usage
    # Make sure Neo4j is running and .env file is configured or env vars are set
    logging.basicConfig(level=logging.INFO)
    
    # Create dummy gtd file for testing
    with open("gtd_test.txt", "w") as f:
        f.write("Task 1 #project - Discuss budget with @john for #project-alpha\n")
        f.write("  Subtask 1.1 - Prepare slides\n")
        f.write("    Subtask 1.1.1 #detail - Draft initial version\n")
        f.write("  Subtask 1.2\n")
        f.write("Task 2 #another - Plan team offsite\n")

    try:
        neo4j_client = Neo4jClient()
        ollama_client = OllamaLLM()
        # Check if ollama is running
        if not ollama_client.health_check():
            logger.error("Ollama is not running. Please start Ollama to run this script.")
        else:
            ingestion_service = GraphIngestionService(neo4j_client, ollama_client)
            ingestion_service.ingest_gtd_file("gtd_test.txt")
            print("Ingestion successful. Check your Neo4j browser.")
    except Exception as e:
        logger.error(f"An error occurred during ingestion: {e}", exc_info=True)
    finally:
        if 'neo4j_client' in locals() and neo4j_client:
            neo4j_client.close() 