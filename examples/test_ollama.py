#!/usr/bin/env python3
"""
Test script for Ollama integration.
This script tests the OllamaLLM client and verifies connectivity.
"""

import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm.ollama_client import OllamaLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ollama_connection():
    """Test basic Ollama connectivity."""
    try:
        # Use the smaller qwen3:1.7b model to avoid memory issues
        client = OllamaLLM(model='qwen3:1.7b')
        
        # Test health check
        logger.info("Testing Ollama health check...")
        if client.health_check():
            logger.info("✅ Ollama service is healthy")
        else:
            logger.error("❌ Ollama service is not healthy")
            return False
        
        # List available models
        logger.info("Listing available models...")
        models = client.list_models()
        logger.info(f"Available models: {models}")
        
        # Test model info
        logger.info("Getting model info...")
        model_info = client.get_model_info()
        if model_info:
            logger.info(f"✅ Model info retrieved: {model_info.get('name', 'Unknown')}")
        else:
            logger.warning("⚠️ Could not retrieve model info")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def test_text_generation():
    """Test text generation with Ollama."""
    try:
        # Use the smaller qwen3:1.7b model to avoid memory issues
        client = OllamaLLM(model='qwen3:1.7b')
        
        # Simple test prompt
        test_prompt = "Hello! Please respond with a short greeting."
        
        logger.info(f"Testing text generation with prompt: '{test_prompt}'")
        response = client.generate(test_prompt, temperature=0.7, max_tokens=50)
        
        logger.info(f"✅ Generated response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Text generation test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting Ollama integration tests...")
    
    # Test 1: Connection
    if not test_ollama_connection():
        logger.error("Connection test failed. Make sure Ollama is running.")
        sys.exit(1)
    
    # Test 2: Text generation
    if not test_text_generation():
        logger.error("Text generation test failed.")
        sys.exit(1)
    
    logger.info("🎉 All tests passed! Ollama integration is working correctly.")


if __name__ == "__main__":
    main() 