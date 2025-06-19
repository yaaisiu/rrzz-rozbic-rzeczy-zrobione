import requests
import json
import logging
import os
from typing import Any, Dict, Optional
from .base import BaseLLM

logger = logging.getLogger(__name__)


class OllamaLLM(BaseLLM):
    """Ollama LLM client for interacting with local Ollama service."""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout: int = 120):
        """
        Initialize Ollama LLM client.
        
        Args:
            base_url: Ollama API base URL (defaults to config or http://localhost:11434)
            model: Model name to use (defaults to config or qwen3:0.6b)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'qwen3:0.6b')
        self.timeout = timeout
        
        # Ensure base_url doesn't end with slash
        self.base_url = self.base_url.rstrip('/')
        
        logger.info(f"Initialized Ollama client with base_url={self.base_url}, model={self.model}")
    
    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None, method: str = 'POST') -> Dict[str, Any]:
        """
        Make HTTP request to Ollama API.
        
        Args:
            endpoint: API endpoint (e.g., '/api/generate')
            data: Request payload (for POST requests)
            method: HTTP method ('GET' or 'POST')
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
            else:  # POST
                response = requests.post(
                    url,
                    json=data,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using Ollama model.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        # Always add think: False for Qwen models
        if self.model.startswith("qwen"):
            payload["think"] = False

        # Add optional parameters
        if 'temperature' in kwargs:
            payload['options'] = {'temperature': kwargs['temperature']}
        if 'max_tokens' in kwargs:
            payload['options'] = payload.get('options', {})
            payload['options']['num_predict'] = kwargs['max_tokens']
        
        try:
            logger.debug(f"Generating with Ollama model {self.model}")
            response = self._make_request('/api/generate', payload)
            
            # Handle the actual Ollama API response format
            if 'response' in response:
                return response['response']
            elif 'error' in response:
                logger.error(f"Ollama API error: {response['error']}")
                raise Exception(f"Ollama API error: {response['error']}")
            else:
                logger.error(f"Unexpected Ollama response format: {response}")
                raise Exception("Invalid response format from Ollama API")
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    def list_models(self) -> list:
        """
        List available models.
        
        Returns:
            List of available model names
        """
        try:
            # Use GET request for /api/tags in Ollama v0.9.x
            response = self._make_request('/api/tags', method='GET')
            return [model['name'] for model in response.get('models', [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Check if Ollama service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Use GET request for /api/tags in Ollama v0.9.x
            self._make_request('/api/tags', method='GET')
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Model information dictionary
        """
        try:
            # Use POST request for /api/show
            response = self._make_request('/api/show', {'name': self.model})
            return response
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {} 