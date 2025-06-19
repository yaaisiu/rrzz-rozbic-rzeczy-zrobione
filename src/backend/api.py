from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion import NoteIngestionService
from graph.neo4j_client import Neo4jClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Note Ingestion API", version="1.0.0")

# Initialize services
ingestion_service = NoteIngestionService()
neo4j_client = Neo4jClient()


class NoteRequest(BaseModel):
    """Request model for note submission."""
    content: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    """Response model for note processing."""
    note_id: str
    content: str
    tags: List[str]
    entities: List[Dict[str, str]]
    highlights: List[str]
    status: str
    processed_at: str
    error: Optional[str] = None


class SearchRequest(BaseModel):
    """Request model for note search."""
    query: str
    limit: Optional[int] = 10


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint."""
    try:
        # Check Neo4j connection
        neo4j_healthy = neo4j_client.health_check()
        
        return {
            "status": "ok",
            "neo4j": "healthy" if neo4j_healthy else "unhealthy",
            "ingestion_service": "ready"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/notes", response_model=NoteResponse)
async def ingest_note(note_request: NoteRequest) -> NoteResponse:
    """
    Ingest a new note into the knowledge graph.
    
    Args:
        note_request: Note content and optional metadata
        
    Returns:
        Processing result with extracted tags, entities, and highlights
    """
    try:
        logger.info(f"Received note ingestion request: {note_request.content[:100]}...")
        
        # Process the note through the ingestion service
        result = ingestion_service.ingest_note(note_request.content)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])
        
        # Convert to response model
        response = NoteResponse(
            note_id=result['note_id'],
            content=result['content'],
            tags=result['tags'],
            entities=result['entities'],
            highlights=result['highlights'],
            status=result['status'],
            processed_at=result['processed_at']
        )
        
        logger.info(f"Successfully processed note with ID: {result['note_id']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest note: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest note: {str(e)}")


@app.post("/notes/batch", response_model=List[NoteResponse])
async def batch_ingest_notes(notes: List[NoteRequest]) -> List[NoteResponse]:
    """
    Ingest multiple notes in batch.
    
    Args:
        notes: List of note requests
        
    Returns:
        List of processing results
    """
    try:
        logger.info(f"Received batch ingestion request for {len(notes)} notes")
        
        # Extract note contents
        note_contents = [note.content for note in notes]
        
        # Process notes in batch
        results = ingestion_service.batch_ingest_notes(note_contents)
        
        # Convert to response models
        responses = []
        for result in results:
            if result['status'] == 'error':
                response = NoteResponse(
                    note_id="",
                    content=result['content'],
                    tags=[],
                    entities=[],
                    highlights=[],
                    status="error",
                    processed_at="",
                    error=result['error']
                )
            else:
                response = NoteResponse(
                    note_id=result['note_id'],
                    content=result['content'],
                    tags=result['tags'],
                    entities=result['entities'],
                    highlights=result['highlights'],
                    status=result['status'],
                    processed_at=result['processed_at']
                )
            responses.append(response)
        
        logger.info(f"Successfully processed {len(responses)} notes")
        return responses
        
    except Exception as e:
        logger.error(f"Failed to batch ingest notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to batch ingest notes: {str(e)}")


@app.get("/notes/{note_id}", response_model=Dict[str, Any])
async def get_note(note_id: str) -> Dict[str, Any]:
    """
    Retrieve a note by ID.
    
    Args:
        note_id: The note ID to retrieve
        
    Returns:
        Note data with metadata
    """
    try:
        note = neo4j_client.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
        
        return note
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve note: {str(e)}")


@app.post("/notes/search", response_model=List[Dict[str, Any]])
async def search_notes(search_request: SearchRequest) -> List[Dict[str, Any]]:
    """
    Search notes by content or tags.
    
    Args:
        search_request: Search query and limit
        
    Returns:
        List of matching notes
    """
    try:
        limit = search_request.limit or 10
        notes = neo4j_client.search_notes(search_request.query, limit)
        return notes
        
    except Exception as e:
        logger.error(f"Failed to search notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search notes: {str(e)}")


@app.get("/notes", response_model=List[Dict[str, Any]])
async def list_notes(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List recent notes.
    
    Args:
        limit: Maximum number of notes to return
        offset: Number of notes to skip
        
    Returns:
        List of recent notes
    """
    try:
        # For now, return empty list - this can be implemented later
        # TODO: Implement pagination in Neo4j client
        return []
        
    except Exception as e:
        logger.error(f"Failed to list notes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list notes: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    try:
        ingestion_service.close()
        neo4j_client.close()
        logger.info("API shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}") 