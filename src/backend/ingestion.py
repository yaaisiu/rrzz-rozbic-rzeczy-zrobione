"""
Handles note ingestion, chunking, embedding, and upserting into Neo4j.
"""

import logging
import json
import re
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.ollama_client import OllamaLLM
from graph.neo4j_client import Neo4jClient
from utils.config_loader import load_yaml_config

logger = logging.getLogger(__name__)


class NoteIngestionService:
    """Service for processing and ingesting notes into the knowledge graph."""
    
    def __init__(self):
        """Initialize the ingestion service with LLM and Neo4j clients."""
        self.llm_client = OllamaLLM()
        self.neo4j_client = Neo4jClient()
        
        # Load prompt templates
        self.prompt_templates = load_yaml_config('config/prompt_templates.yaml')
        
        logger.info("NoteIngestionService initialized")
    
    def _extract_tags_and_entities(self, note_content: str) -> Dict[str, Any]:
        """
        Extract tags and entities from note content using LLM.
        
        Args:
            note_content: The note text to process
            
        Returns:
            Dictionary containing tags and entities
        """
        try:
            # Prepare the tagging prompt
            tagging_prompt = self.prompt_templates['tagging_prompt'].format(note=note_content)
            
            # Get LLM response
            response = self.llm_client.generate(tagging_prompt, temperature=0.3)
            
            # Parse the response to extract tags and entities
            # For now, we'll use a simple approach - extract tags and entities from the response
            tags = self._extract_tags_from_response(response)
            entities = self._extract_entities_from_response(response)
            
            return {
                'tags': tags,
                'entities': entities
            }
            
        except Exception as e:
            logger.error(f"Failed to extract tags and entities: {e}")
            return {'tags': [], 'entities': []}
    
    def _extract_tags_from_response(self, response: str) -> List[str]:
        """
        Extract tags from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            List of extracted tags
        """
        # Simple tag extraction - look for words that might be tags
        # This is a basic implementation that can be improved
        words = re.findall(r'\b\w+\b', response.lower())
        
        # Filter out common words and short words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'}
        
        tags = []
        for word in words:
            if len(word) > 2 and word not in common_words:
                # Check if it looks like a tag (capitalized or has special meaning)
                if word.isupper() or word in response:  # Simple heuristic
                    tags.append(word)
        
        # Limit to top 10 tags
        return list(set(tags))[:10]
    
    def _extract_entities_from_response(self, response: str) -> List[Dict[str, str]]:
        """
        Extract entities from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            List of entity dictionaries with name and type
        """
        # Simple entity extraction - look for capitalized words that might be entities
        # This is a basic implementation that can be improved
        entities = []
        
        # Look for capitalized words (potential proper nouns)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', response)
        
        for word in capitalized_words:
            if len(word) > 2:
                # Simple entity type detection
                entity_type = 'unknown'
                if word.endswith('ing'):
                    entity_type = 'action'
                elif word[0].isupper() and word[1:].islower():
                    entity_type = 'person'
                elif word.isupper():
                    entity_type = 'organization'
                
                entities.append({
                    'name': word,
                    'type': entity_type
                })
        
        # Limit to top 10 entities
        return entities[:10]
    
    def _generate_highlights(self, note_content: str) -> List[str]:
        """
        Generate highlights for important phrases in the note.
        
        Args:
            note_content: The note text to highlight
            
        Returns:
            List of highlighted phrases
        """
        try:
            # Prepare the highlighting prompt
            highlighting_prompt = self.prompt_templates['highlighting_prompt'].format(note=note_content)
            
            # Get LLM response
            response = self.llm_client.generate(highlighting_prompt, temperature=0.2)
            
            # Extract highlighted phrases (simple approach)
            # Look for phrases that might be highlighted
            highlights = []
            
            # Split into sentences and look for important ones
            sentences = re.split(r'[.!?]+', response)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # Only consider substantial sentences
                    # Look for words that might indicate importance
                    important_indicators = ['important', 'key', 'critical', 'essential', 'significant', 'major', 'primary', 'main']
                    if any(indicator in sentence.lower() for indicator in important_indicators):
                        highlights.append(sentence)
            
            return highlights[:5]  # Limit to 5 highlights
            
        except Exception as e:
            logger.error(f"Failed to generate highlights: {e}")
            return []
    
    def _generate_embedding(self, note_content: str) -> List[float]:
        """
        Generate embedding for the note content.
        
        Args:
            note_content: The note text to embed
            
        Returns:
            List of embedding values (placeholder for now)
        """
        # TODO: Implement actual embedding generation
        # For now, return a placeholder embedding
        # This should be replaced with actual embedding generation using a model
        return [0.0] * 384  # Placeholder 384-dimensional embedding
    
    def ingest_note(self, note_content: str) -> Dict[str, Any]:
        """
        Process and ingest a note into the knowledge graph.
        
        Args:
            note_content: The note text to process
            
        Returns:
            Dictionary containing processing results and note ID
        """
        try:
            logger.info(f"Starting ingestion of note: {note_content[:100]}...")
            
            # Step 1: Extract tags and entities
            extraction_result = self._extract_tags_and_entities(note_content)
            tags = extraction_result['tags']
            entities = extraction_result['entities']
            
            # Step 2: Generate highlights
            highlights = self._generate_highlights(note_content)
            
            # Step 3: Generate embedding
            embedding = self._generate_embedding(note_content)
            
            # Step 4: Prepare metadata
            metadata = {
                'tags': tags,
                'entities': entities,
                'highlights': highlights,
                'embedding': embedding,
                'processed_at': datetime.now().isoformat()
            }
            
            # Step 5: Upsert to Neo4j
            note_id = self.neo4j_client.upsert_note(note_content, metadata)
            
            result = {
                'note_id': note_id,
                'content': note_content,
                'tags': tags,
                'entities': entities,
                'highlights': highlights,
                'status': 'success',
                'processed_at': metadata['processed_at']
            }
            
            logger.info(f"Successfully ingested note with ID: {note_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to ingest note: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'content': note_content
            }
    
    def batch_ingest_notes(self, notes: List[str]) -> List[Dict[str, Any]]:
        """
        Process and ingest multiple notes.
        
        Args:
            notes: List of note texts to process
            
        Returns:
            List of processing results
        """
        results = []
        for note in notes:
            result = self.ingest_note(note)
            results.append(result)
        return results
    
    def close(self) -> None:
        """Close connections and cleanup resources."""
        if hasattr(self, 'neo4j_client'):
            self.neo4j_client.close()
        logger.info("NoteIngestionService closed")


# Convenience function for backward compatibility
def ingest_note(note_content: str) -> Dict[str, Any]:
    """
    Convenience function to ingest a single note.
    
    Args:
        note_content: The note text to process
        
    Returns:
        Processing result dictionary
    """
    service = NoteIngestionService()
    try:
        return service.ingest_note(note_content)
    finally:
        service.close() 