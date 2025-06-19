from typing import Any

class BaseLLM:
    """Base class for LLM providers."""
    def generate(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError 