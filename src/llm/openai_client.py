import os
import logging
from openai import OpenAI
from .base import BaseLLM
from typing import Any, Optional

logger = logging.getLogger(__name__)

class OpenAILLM(BaseLLM):
    """OpenAI LLM client for interacting with the OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize OpenAI LLM client.

        Args:
            api_key: OpenAI API Key. Defaults to OPENAI_API_KEY env variable.
            model_name: The name of the model to use. Defaults to OPENAI_MODEL_NAME env var or "gpt-3.5-turbo".
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
        
        self.model_name = model_name or os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"Initialized OpenAI client with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using the configured OpenAI model.

        Args:
            prompt: Input prompt for the model.
            **kwargs: Additional parameters for the chat completion (e.g., temperature).

        Returns:
            Generated text response.
        """
        try:
            logger.debug(f"Generating with OpenAI model {self.model_name}")
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides structured data."},
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            
            if completion.choices and completion.choices[0].message:
                response = completion.choices[0].message.content
                if response:
                    return response.strip()

            logger.warning("OpenAI response was empty.")
            return "[No response from OpenAI]"
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise 