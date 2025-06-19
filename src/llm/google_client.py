import os
import logging
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerationConfig
from .base import BaseLLM
from typing import Any, Optional

logger = logging.getLogger(__name__)

class GoogleLLM(BaseLLM):
    """Google LLM client for interacting with the Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Google LLM client.

        Args:
            api_key: Google API Key. Defaults to GOOGLE_API_KEY env variable.
            model_name: The name of the model to use. Defaults to GOOGLE_MODEL_NAME env var or "gemini-2.5-flash".
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is not set. Please set the GOOGLE_API_KEY environment variable.")

        # Get model name from args, then env var, then default
        self.model_name = model_name or os.getenv('GOOGLE_MODEL_NAME', 'gemini-2.5-flash')
        
        # --- Debugging ---
        logger.info(f"GoogleLLM: API key loaded: {'Yes' if self.api_key else 'No'}")
        logger.info(f"GoogleLLM: Model name: {self.model_name}")
        # --- End Debugging ---

        try:
            configure(api_key=self.api_key)
            self.model = GenerativeModel(self.model_name)
            logger.info(f"Initialized Google Gemini client with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Google Gemini client: {e}")
            raise

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using the configured Gemini model.

        Args:
            prompt: Input prompt for the model.
            **kwargs: Additional parameters for the generation config (e.g., temperature).

        Returns:
            Generated text response.

        Raises:
            Exception: If generation fails.
        """
        try:
            logger.debug(f"Generating with Google Gemini model {self.model_name}")
            # Construct generation_config from kwargs
            generation_config = GenerationConfig(**kwargs) if kwargs else None

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Accessing the text from the response
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                # Handle cases where the prompt might be blocked
                logger.warning(f"Gemini response has no content. Prompt may have been blocked. Details: {response.prompt_feedback}")
                return f"[Gemini Safety Block: {response.prompt_feedback}]"

        except Exception as e:
            logger.error(f"Google Gemini text generation failed: {e}")
            raise 