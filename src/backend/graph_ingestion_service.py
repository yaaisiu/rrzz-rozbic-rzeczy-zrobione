import logging
import json
import re
from typing import List, Dict, Any, Set

from src.backend.file_parser import parse_file, Note
from src.graph.neo4j_client import Neo4jClient
from src.llm.base import BaseLLM

logger = logging.getLogger(__name__)

class GraphIngestionService:
    def __init__(self, neo4j_client: Neo4jClient, llm_client: BaseLLM):
        self.client = neo4j_client
        self.llm_client = llm_client

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
            json_match = re.search(r'{.*}', llm_response_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logger.warning(f"Could not find a JSON object in the LLM response for note: {note.content_hash[:7]}")
                return {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response for note {note.content_hash[:7]}: {llm_response_str}")
            return {}

    def _process_new_notes(self, notes: List[Note]):
        """Processes and ingests only the notes that are new."""
        if not notes:
            logger.info("No new notes to process.")
            return

        logger.info(f"Processing {len(notes)} new notes...")
        for i, note in enumerate(notes):
            logger.info(f"[{i+1}/{len(notes)}] Processing new note from {note.date_str} (hash: {note.content_hash[:7]})")
            
            llm_metadata = self._get_llm_metadata(note)

            query = """
            MERGE (n:GtdNote {content_hash: $content_hash})
            ON CREATE SET
                n.content = $content,
                n.line_number = $line_number,
                n.llm_summary = $llm_summary,
                n.created_at = datetime()
            MERGE (d:Day {date: $date_str})
            MERGE (n)-[:RECORDED_ON]->(d)
            
            WITH n, $tags as tags, $entities as entities
            FOREACH (tag_name IN tags |
                MERGE (t:Tag {name: tag_name})
                MERGE (n)-[:HAS_TAG]->(t)
            )
            FOREACH (entity IN entities |
                MERGE (e:Entity {name: entity.name})
                ON CREATE SET e.type = entity.type
                MERGE (n)-[:MENTIONS]->(e)
            )
            """
            params = {
                "content_hash": note.content_hash,
                "content": note.content,
                "line_number": note.line_number,
                "date_str": note.date_str,
                "llm_summary": llm_metadata.get("summary", ""),
                "tags": note.tags,
                "entities": llm_metadata.get("entities", [])
            }
            self.client.execute_query(query, params)
        logger.info(f"Finished processing {len(notes)} new notes.")

    def _update_existing_notes(self, notes: List[Note]):
        """Updates the line_number for notes that already exist in the graph but may have moved."""
        if not notes:
            return
            
        logger.info(f"Updating line numbers for {len(notes)} existing notes...")
        query = """
        UNWIND $notes as note_data
        MATCH (n:GtdNote {content_hash: note_data.content_hash})
        SET n.line_number = note_data.line_number
        """
        # We only need hash and line number for the update
        notes_data = [{"content_hash": n.content_hash, "line_number": n.line_number} for n in notes]
        self.client.execute_query(query, {"notes": notes_data})
        logger.info("Finished updating line numbers.")

    def _cleanup_deleted_notes(self, deleted_hashes: List[str]):
        """Removes notes from the graph that are no longer in the source file."""
        if not deleted_hashes:
            return

        logger.info(f"Cleaning up {len(deleted_hashes)} deleted notes...")
        # Delete notes
        query_delete = "MATCH (n:GtdNote) WHERE n.content_hash IN $hashes DETACH DELETE n"
        self.client.execute_query(query_delete, {"hashes": deleted_hashes})
        
        # Delete orphaned nodes
        query_orphans = """
        MATCH (n)
        WHERE (n:Tag OR n:Entity OR n:Day) AND NOT (n)--()
        DELETE n
        """
        self.client.execute_query(query_orphans)
        logger.info("Successfully cleaned up deleted and orphaned nodes.")

    def build_hierarchy(self, notes: List[Note]):
        """Builds HAS_CHILD relationships based on indentation using content_hash."""
        if not notes:
            return
            
        logger.info("Building note hierarchy...")
        # Clear all existing hierarchy relationships first
        self.client.execute_query("MATCH ()-[r:HAS_CHILD]->() DELETE r")
        
        parent_stack = []  # Stack of (indentation, content_hash)

        for note in notes:
            while parent_stack and parent_stack[-1][0] >= note.indentation:
                parent_stack.pop()

            if parent_stack:
                parent_hash = parent_stack[-1][1]
                query = """
                MATCH (parent:GtdNote {content_hash: $parent_hash})
                MATCH (child:GtdNote {content_hash: $child_hash})
                MERGE (parent)-[:HAS_CHILD]->(child)
                """
                params = {"parent_hash": parent_hash, "child_hash": note.content_hash}
                self.client.execute_query(query, params)

            parent_stack.append((note.indentation, note.content_hash))
        logger.info("Successfully built note hierarchy.")

    def ingest_gtd_file(self, file_path: str):
        """
        Parses a GTD file and incrementally updates the graph using content hashing
        to be resilient to line number changes.
        """
        logger.info(f"Starting resilient ingestion for file: {file_path}")
        
        # 1. Get current state from file and graph
        notes_from_file = parse_file(file_path)
        file_hashes: Set[str] = {note.content_hash for note in notes_from_file}
        
        graph_notes_raw = self.client.execute_query("MATCH (n:GtdNote) RETURN n.content_hash AS content_hash")
        graph_hashes: Set[str] = {item['content_hash'] for item in graph_notes_raw if item['content_hash']}

        # 2. Determine what's new, deleted, and existing
        new_hashes = file_hashes - graph_hashes
        deleted_hashes = graph_hashes - file_hashes
        existing_hashes = file_hashes.intersection(graph_hashes)
        
        logger.info(f"Found {len(new_hashes)} new, {len(deleted_hashes)} deleted, and {len(existing_hashes)} existing notes.")

        # 3. Create notes to add and update
        notes_to_add = [note for note in notes_from_file if note.content_hash in new_hashes]
        notes_to_update = [note for note in notes_from_file if note.content_hash in existing_hashes]

        # 4. Execute pipeline
        self._process_new_notes(notes_to_add)
        self._update_existing_notes(notes_to_update)
        self._cleanup_deleted_notes(list(deleted_hashes))
        
        # 5. Rebuild the entire hierarchy for all notes currently in the file
        self.build_hierarchy(notes_from_file)
          
        logger.info(f"Finished resilient ingestion for file: {file_path}") 