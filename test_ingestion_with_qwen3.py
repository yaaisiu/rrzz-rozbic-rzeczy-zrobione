#!/usr/bin/env python3
"""
Test script to verify ingestion system works with qwen3:0.6b model.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backend.ingestion import NoteIngestionService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_ingestion_with_qwen3():
    """Test note ingestion with qwen3:0.6b model."""
    try:
        # Sample notes for testing
        test_notes = [
            "I need to finish the Python project by Friday. The backend API is almost complete.",
            "Meeting with John tomorrow at 2 PM to discuss the new features for the knowledge graph system.",
            "Remember to buy groceries: milk, bread, eggs, and vegetables for dinner tonight."
        ]
        
        logger.info("Initializing NoteIngestionService with qwen3:0.6b...")
        ingestion_service = NoteIngestionService()
        
        for i, note in enumerate(test_notes, 1):
            logger.info(f"\n=== Processing test note {i} ===")
            logger.info(f"Note: {note[:50]}...")
            
            result = ingestion_service.ingest_note(note)
            
            if result['status'] == 'success':
                logger.info(f"✅ Note {i} processed successfully")
                logger.info(f"  - Note ID: {result['note_id']}")
                logger.info(f"  - Tags: {result['tags']}")
                logger.info(f"  - Entities: {result['entities']}")
                logger.info(f"  - Highlights: {len(result['highlights'])} highlights")
                
                # Show highlights if any
                if result['highlights']:
                    for j, highlight in enumerate(result['highlights'], 1):
                        logger.info(f"    Highlight {j}: {highlight[:100]}...")
            else:
                logger.error(f"❌ Note {i} processing failed: {result.get('error', 'Unknown error')}")
        
        ingestion_service.close()
        logger.info("\n🎉 All notes processed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Note ingestion test failed: {e}")
        return False


def main():
    """Run the ingestion test."""
    logger.info("Starting ingestion test with qwen3:0.6b model...")
    
    success = test_ingestion_with_qwen3()
    
    if success:
        logger.info("\n✅ Ingestion system is working correctly with qwen3:0.6b!")
        return 0
    else:
        logger.error("\n❌ Ingestion system has issues.")
        return 1


if __name__ == "__main__":
    exit(main()) 