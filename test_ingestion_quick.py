#!/usr/bin/env python3
"""
Quick test script for ingestion with qwen3:0.6b model and longer timeout.
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


def test_single_note():
    """Test ingestion of a single note with the working model."""
    try:
        # Simple test note
        test_note = "I need to finish the Python project by Friday. The backend API is almost complete."
        
        logger.info("Testing ingestion with qwen3:0.6b model...")
        logger.info(f"Note: {test_note}")
        
        ingestion_service = NoteIngestionService()
        
        logger.info("Processing note (this may take 10-15 seconds)...")
        result = ingestion_service.ingest_note(test_note)
        
        if result['status'] == 'success':
            logger.info("✅ Note processed successfully!")
            logger.info(f"  - Note ID: {result['note_id']}")
            logger.info(f"  - Tags: {result['tags']}")
            logger.info(f"  - Entities: {result['entities']}")
            logger.info(f"  - Highlights: {len(result['highlights'])} highlights")
            
            # Show highlights if any
            if result['highlights']:
                for i, highlight in enumerate(result['highlights'], 1):
                    logger.info(f"    Highlight {i}: {highlight[:100]}...")
        else:
            logger.error(f"❌ Note processing failed: {result.get('error', 'Unknown error')}")
        
        ingestion_service.close()
        return result['status'] == 'success'
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def main():
    """Run the quick test."""
    logger.info("Starting quick ingestion test with qwen3:0.6b...")
    
    success = test_single_note()
    
    if success:
        logger.info("\n🎉 Success! The ingestion system is working with qwen3:0.6b!")
        return 0
    else:
        logger.error("\n❌ Test failed.")
        return 1


if __name__ == "__main__":
    exit(main()) 