from .base import BaseLLM

class OpenAILLM(BaseLLM):
    """OpenAI LLM client stub."""
    def generate(self, prompt: str, **kwargs):
        # TODO: Implement call to OpenAI API
        return "[OpenAI response stub]" 