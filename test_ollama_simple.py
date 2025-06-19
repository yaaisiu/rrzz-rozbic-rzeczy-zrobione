#!/usr/bin/env python3
"""
Simple test script to debug Ollama LLM issues.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm.ollama_client import OllamaLLM

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_ollama_basic():
    """Test basic Ollama functionality with simple questions."""
    try:
        # Initialize Ollama client with qwen3:0.6b model
        llm = OllamaLLM(model="qwen3:0.6b")
        
        # Test health check
        logger.info("Testing Ollama health check...")
        health = llm.health_check()
        logger.info(f"Health check result: {'PASS' if health else 'FAIL'}")
        
        if not health:
            logger.error("Ollama is not healthy, cannot proceed with tests")
            return False
        
        # Test 1: Simple question
        logger.info("\n=== Test 1: Simple Question ===")
        question1 = "What is 2 + 2?"
        logger.info(f"Question: {question1}")
        
        try:
            response1 = llm.generate(question1, temperature=0.1)
            logger.info(f"Response: {response1}")
        except Exception as e:
            logger.error(f"Failed to get response for question 1: {e}")
            return False
        
        # Test 2: More complex question
        logger.info("\n=== Test 2: Complex Question ===")
        question2 = "Extract the main topics from this text: 'I need to finish the Python project by Friday. The backend API is almost complete.'"
        logger.info(f"Question: {question2}")
        
        try:
            response2 = llm.generate(question2, temperature=0.3)
            logger.info(f"Response: {response2}")
        except Exception as e:
            logger.error(f"Failed to get response for question 2: {e}")
            return False
        
        # Test 3: List available models
        logger.info("\n=== Test 3: List Models ===")
        try:
            models = llm.list_models()
            logger.info(f"Available models: {models}")
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
        
        # Test 4: Get model info
        logger.info("\n=== Test 4: Model Info ===")
        try:
            model_info = llm.get_model_info()
            logger.info(f"Model info: {model_info}")
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
        
        logger.info("\n🎉 All Ollama tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Ollama test failed: {e}")
        return False


def test_ollama_with_different_models():
    """Test with different model configurations."""
    logger.info("\n=== Testing Different Model Configurations ===")
    
    # Test with qwen3:0.6b model (working model)
    logger.info("Testing with qwen3:0.6b model...")
    llm_qwen3_06 = OllamaLLM(model="qwen3:0.6b")
    try:
        response = llm_qwen3_06.generate("Hello, how are you?", temperature=0.1)
        logger.info(f"qwen3:0.6b response: {response[:100]}...")
    except Exception as e:
        logger.error(f"qwen3:0.6b model failed: {e}")
    
    # Test with qwen3:1.7b model (memory issues)
    logger.info("Testing with qwen3:1.7b model...")
    llm_qwen3_17 = OllamaLLM(model="qwen3:1.7b")
    try:
        response = llm_qwen3_17.generate("Hello, how are you?", temperature=0.1)
        logger.info(f"qwen3:1.7b response: {response[:100]}...")
    except Exception as e:
        logger.error(f"qwen3:1.7b model failed: {e}")
    
    # Test with default model (qwen2.5:3b - memory issues)
    logger.info("Testing with default model (qwen2.5:3b)...")
    llm_default = OllamaLLM()
    try:
        response = llm_default.generate("Hello, how are you?", temperature=0.1)
        logger.info(f"Default model response: {response[:100]}...")
    except Exception as e:
        logger.error(f"Default model failed: {e}")


def main():
    """Run all Ollama tests."""
    logger.info("Starting Ollama debugging tests with qwen3:0.6b...")
    
    # Test basic functionality
    basic_ok = test_ollama_basic()
    
    # Test different model configurations
    test_ollama_with_different_models()
    
    if basic_ok:
        logger.info("\n✅ Ollama is working correctly with qwen3:0.6b!")
        return 0
    else:
        logger.error("\n❌ Ollama has issues that need to be resolved.")
        return 1


if __name__ == "__main__":
    exit(main()) 