import logging
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase
import os

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j client for graph database operations."""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j client.
        
        Args:
            uri: Neo4j connection URI (defaults to environment variable)
            user: Neo4j username (defaults to environment variable)
            password: Neo4j password (defaults to environment variable)
        """
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = None
        self._connect()
        
        logger.info(f"Initialized Neo4j client with URI: {self.uri}")
    
    def _connect(self) -> None:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def upsert_note(self, note_content: str, metadata: Dict[str, Any]) -> str:
        """
        Upsert a note into the knowledge graph.
        
        Args:
            note_content: The note text content
            metadata: Dictionary containing tags, entities, highlights, etc.
            
        Returns:
            The ID of the created/updated note node
        """
        with self.driver.session() as session:
            # Create or update the note node
            result = session.run("""
                MERGE (n:Note {content: $content})
                ON CREATE SET 
                    n.id = randomUUID(),
                    n.created_at = datetime(),
                    n.tags = $tags,
                    n.highlights = $highlights,
                    n.embedding = $embedding
                ON MATCH SET 
                    n.updated_at = datetime(),
                    n.tags = $tags,
                    n.highlights = $highlights,
                    n.embedding = $embedding
                RETURN n.id as note_id
            """, {
                'content': note_content,
                'tags': metadata.get('tags', []),
                'highlights': metadata.get('highlights', []),
                'embedding': metadata.get('embedding', [])
            })
            
            note_id = result.single()['note_id']
            
            # Create tag nodes and relationships
            for tag in metadata.get('tags', []):
                session.run("""
                    MERGE (t:Tag {name: $tag_name})
                    MERGE (n:Note {id: $note_id})
                    MERGE (n)-[:TAGGED_WITH]->(t)
                """, {'tag_name': tag, 'note_id': note_id})
            
            # Create entity nodes and relationships
            for entity in metadata.get('entities', []):
                # Handle entity as either a string or a dictionary
                if isinstance(entity, dict):
                    entity_name = entity.get('name', '')
                    entity_type = entity.get('type', 'unknown')
                else:
                    entity_name = str(entity)
                    entity_type = 'unknown'
                
                session.run("""
                    MERGE (e:Entity {name: $entity_name, type: $entity_type})
                    MERGE (n:Note {id: $note_id})
                    MERGE (n)-[:MENTIONS]->(e)
                """, {
                    'entity_name': entity_name,
                    'entity_type': entity_type,
                    'note_id': note_id
                })
            
            logger.info(f"Successfully upserted note with ID: {note_id}")
            return note_id
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a note by ID.
        
        Args:
            note_id: The note ID
            
        Returns:
            Note data dictionary or None if not found
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note {id: $note_id})
                OPTIONAL MATCH (n)-[:TAGGED_WITH]->(t:Tag)
                OPTIONAL MATCH (n)-[:MENTIONS]->(e:Entity)
                RETURN n, collect(DISTINCT t.name) as tags, collect(DISTINCT e) as entities
            """, {'note_id': note_id})
            
            record = result.single()
            if record:
                note = record['n']
                return {
                    'id': note['id'],
                    'content': note['content'],
                    'tags': record['tags'],
                    'entities': record['entities'],
                    'created_at': note.get('created_at'),
                    'updated_at': note.get('updated_at')
                }
            return None
    
    def search_notes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search notes by content or tags.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching notes
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Note)
                WHERE n.content CONTAINS $query 
                   OR ANY(tag IN n.tags WHERE tag CONTAINS $query)
                OPTIONAL MATCH (n)-[:TAGGED_WITH]->(t:Tag)
                OPTIONAL MATCH (n)-[:MENTIONS]->(e:Entity)
                RETURN n, collect(DISTINCT t.name) as tags, collect(DISTINCT e) as entities
                LIMIT $limit
            """, {'query': query, 'limit': limit})
            
            notes = []
            for record in result:
                note = record['n']
                notes.append({
                    'id': note['id'],
                    'content': note['content'],
                    'tags': record['tags'],
                    'entities': record['entities'],
                    'created_at': note.get('created_at'),
                    'updated_at': note.get('updated_at')
                })
            
            return notes
    
    def health_check(self) -> bool:
        """
        Check if Neo4j connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False 