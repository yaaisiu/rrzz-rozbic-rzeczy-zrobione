import logging
import json
import re
from typing import List, Dict, Any

from src.backend.file_parser import parse_file, Note
from src.graph.neo4j_client import Neo4jClient
from src.llm.base import BaseLLM
from src.llm.ollama_client import OllamaLLM

logger = logging.getLogger(__name__)

class GraphIngestionService:
    def __init__(self, neo4j_client: Neo4jClient, llm_client: BaseLLM):
        self.client = neo4j_client
        self.llm_client = llm_client

    def clear_gtd_notes(self):
        """
        Removes all GTD-related nodes and relationships from the graph to
        ensure a clean slate before ingestion. This includes GtdNote nodes
        and any orphaned Tag, Entity, or Day nodes.
        """
        logger.info("Clearing all GTD-related nodes from the graph.")

        # 1. Delete all GtdNote nodes and their relationships
        query_notes = "MATCH (n:GtdNote) DETACH DELETE n"
        self.client.execute_query(query_notes)
        logger.info("Successfully cleared GtdNote nodes.")

        # 2. Delete any orphaned Tag, Entity, or Day nodes that are no longer connected to anything
        query_orphans = """
        MATCH (n)
        WHERE (n:Tag OR n:Entity OR n:Day) AND NOT (n)--()
        DELETE n
        """
        self.client.execute_query(query_orphans)
        logger.info("Successfully cleared orphaned Tag, Entity, and Day nodes.")

    def _get_llm_metadata(self, note: Note) -> Dict[str, Any]:
        """Gets metadata for a note from the LLM."""
        prompt = f"""
        Analyze the following note content and extract structured metadata.
        The content is: "{note.content}"
        Respond with a JSON object containing:
        - "entities": a list of named entities. Each entity should be an object with "name" and "type" (e.g., "Person", "Project", "Technology").
        - "summary": a one-sentence summary of the note.
        
        Example response for "Discuss budget with @john for #project-alpha":
        {{
          "entities": [
            {{"name": "John", "type": "Person"}},
            {{"name": "Project Alpha", "type": "Project"}}
          ],
          "summary": "A task to discuss the budget for Project Alpha with John."
        }}

        Your response must be only the JSON object.
        Note content: "{note.content}"
        """
        llm_response_str = self.llm_client.generate(prompt)
        
        try:
            # Use regex to find the JSON block, even if it's wrapped in markdown
            json_match = re.search(r'{.*}', llm_response_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logger.warning(f"Could not find a JSON object in the LLM response for line {note.line_number}: {llm_response_str}")
                return {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response as JSON for line {note.line_number}, even after cleaning: {llm_response_str}")
            return {}

    def ingest_notes(self, notes: List[Note]) -> List[str]:
        """
        Ingests a list of notes, creating a rich graph with Day, Note, Tag,
        and Entity nodes and their relationships.
        """
        node_ids: List[str] = []
        logger.info(f"Starting rich ingestion for {len(notes)} notes...")
        for i, note in enumerate(notes):
            logger.info(f"[{i+1}/{len(notes)}] Processing note from {note.date_str} (line {note.line_number})")

            # 1. Get LLM metadata
            llm_metadata = self._get_llm_metadata(note)

            # 2. Use a single, powerful query to create the entire graph structure for this note
            query = """
            // Find or create the Day node
            MERGE (d:Day {date: $date_str})

            // Find or create the GtdNote and link it to the Day
            MERGE (n:GtdNote {line_number: $line_number})
            ON CREATE SET n.content = $content, n.llm_summary = $llm_summary, n.created_at = datetime()
            ON MATCH SET n.content = $content, n.llm_summary = $llm_summary, n.updated_at = datetime()
            MERGE (n)-[:RECORDED_ON]->(d)
            WITH n

            // Process and link Tags
            FOREACH (tag_name IN $tags |
                MERGE (t:Tag {name: tag_name})
                MERGE (n)-[:HAS_TAG]->(t)
            )

            // Process and link Entities
            FOREACH (entity IN $entities |
                MERGE (e:Entity {name: entity.name})
                ON CREATE SET e.type = entity.type
                MERGE (n)-[:MENTIONS]->(e)
            )
            RETURN elementId(n) as node_id
            """
            params = {
                "date_str": note.date_str,
                "line_number": note.line_number,
                "content": note.content,
                "llm_summary": llm_metadata.get("summary", ""),
                "tags": note.tags,
                "entities": llm_metadata.get("entities", [])
            }
            result = self.client.execute_query(query, params)
            if result:
                node_ids.append(result[0]['node_id'])
        
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