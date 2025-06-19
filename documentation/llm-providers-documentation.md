# LLM Provider Documentation

This document provides a comprehensive guide to configuring and using the various Large Language Model (LLM) providers integrated into this project. It covers the setup for Google Gemini, OpenAI, and Ollama, including environment variables and code examples.

## LLM Provider Factory

The project uses a factory pattern to create and manage LLM clients, making it easy to switch between providers. The `get_llm_client()` function in `src/llm/factory.py` determines which client to initialize based on the `LLM_PROVIDER` environment variable.

### Configuration

-   **`LLM_PROVIDER`**: Specifies the LLM provider to use.
    -   **Values**: `google`, `openai`, `ollama`
    -   **Default**: `google`

### Example

To select a provider, set the `LLM_PROVIDER` environment variable:

```bash
export LLM_PROVIDER=openai
```

The application will then use the corresponding client for all LLM-related tasks.

---

## Google Gemini

The `GoogleLLM` client (`src/llm/google_client.py`) interfaces with the Google Gemini API.

### Configuration

-   **`GOOGLE_API_KEY`**: Your Google API key. This is a mandatory environment variable.
-   **`GOOGLE_MODEL_NAME`**: The specific Gemini model to use.
    -   **Default**: `gemini-1.5-flash`

### Usage Example

The following example demonstrates how to initialize the `GoogleLLM` client and generate text.

```python
import os
from src.llm.google_client import GoogleLLM

# Make sure to set the GOOGLE_API_KEY environment variable
# export GOOGLE_API_KEY="your-google-api-key"

try:
    # Initialize the client (will use environment variables)
    google_llm = GoogleLLM()

    # Generate text
    prompt = "Explain the importance of Large Language Models in 50 words."
    response = google_llm.generate(prompt, temperature=0.8)
    
    print(f"Generated Response:\\n{response}")

except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

---

## OpenAI

The `OpenAILLM` client (`src/llm/openai_client.py`) connects to the OpenAI API.

### Configuration

-   **`OPENAI_API_KEY`**: Your OpenAI API key. This is a mandatory environment variable.
-   **`OPENAI_MODEL_NAME`**: The OpenAI model to use.
    -   **Default**: `gpt-3.5-turbo`

### Usage Example

Here's how to use the `OpenAILLM` client for text generation.

```python
import os
from src.llm.openai_client import OpenAILLM

# Make sure to set the OPENAI_API_KEY environment variable
# export OPENAI_API_KEY="your-openai-api-key"

try:
    # Initialize the client
    openai_llm = OpenAILLM()

    # Generate text
    prompt = "Summarize the plot of 'Dune' in three sentences."
    response = openai_llm.generate(prompt, temperature=0.7)
    
    print(f"Generated Response:\\n{response}")

except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

---

## Ollama

The `OllamaLLM` client (`src/llm/ollama_client.py`) allows you to interact with a local Ollama service. This is ideal for development and offline use.

### Configuration

-   **`OLLAMA_BASE_URL`**: The base URL of your Ollama instance.
    -   **Default**: `http://localhost:11434`
-   **`OLLAMA_MODEL`**: The name of the local model to use.
    -   **Default**: `llama2`

### Usage Example

The following example shows how to connect to a local Ollama service, perform a health check, and generate text.

```python
import os
from src.llm.ollama_client import OllamaLLM

# Optional: Set environment variables if not using defaults
# os.environ['OLLAMA_BASE_URL'] = 'http://custom-host:11434'
# os.environ['OLLAMA_MODEL'] = 'mistral'

try:
    # Initialize the client
    ollama_llm = OllamaLLM()

    # 1. Check if the Ollama service is running
    if ollama_llm.health_check():
        print("✅ Ollama service is running.")
    else:
        print("❌ Ollama service is not available. Please start Ollama.")
        exit()

    # 2. List available models
    models = ollama_llm.list_models()
    print(f"Available Ollama models: {models}")

    # 3. Generate text
    prompt = "What is the capital of France?"
    response = ollama_llm.generate(prompt, temperature=0.5, max_tokens=50)
    
    print(f"\\nGenerated Response:\\n{response}")

except Exception as e:
    print(f"An error occurred: {e}") 