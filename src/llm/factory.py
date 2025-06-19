# src/llm/factory.py

import os
import logging
from .base import BaseLLM
from .ollama_client import OllamaLLM
from .openai_client import OpenAILLM
from .google_client import GoogleLLM

logger = logging.getLogger(__name__)

def get_llm_client() -> BaseLLM:
    """
    Factory function to get the appropriate LLM client based on the LLM_PROVIDER environment variable.
    """
    provider = os.getenv('LLM_PROVIDER', 'google').lower()
    logger.info(f"LLM_PROVIDER set to '{provider}'. Initializing client.")

    if provider == 'google':
        return GoogleLLM()
    elif provider == 'openai':
        return OpenAILLM()
    elif provider == 'ollama':
        return OllamaLLM()
    else:
        logger.error(f"Unsupported LLM_PROVIDER '{provider}'. Please check your configuration.")
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}") 