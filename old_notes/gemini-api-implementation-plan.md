# **Integrating Google Gemini API**

This document provides a technical guide to integrate the Google Gemini API into your existing project. It covers updating dependencies, implementing the client, and modifying the application to use the new provider.

### ---

**1\. Update Dependencies**

The official and recommended Python SDK for the Gemini API is google-generativeai. While your requirements.txt file already includes langchain-google-genai, using the native SDK is more direct for this implementation.

Ensure your requirements.txt includes the correct package. If it's not already present, add it:

Plaintext

\# requirements.txt

\# ... existing dependencies  
google-generativeai

Then, update your environment:

Bash

pip install \-r requirements.txt

### **2\. Configure Environment**

To use the Gemini API, you need an API key.

1. **Get an API Key**: If you don't have one, create a key in [Google AI Studio](https://aistudio.google.com/app/apikey).  
2. **Set Environment Variable**: Your application is already set up to load the key from a .env file via the ${GOOGLE\_API\_KEY} variable in config/model\_config.yaml. Add your key to your .env file:  
   Bash  
   \# .env

   \# ... other variables  
   GOOGLE\_API\_KEY="YOUR\_API\_KEY\_HERE"

### **3\. Implement the GoogleLLM Client**

Update the stub file src/llm/google\_client.py with the complete implementation. This code initializes the client using the API key from the environment and wraps the generate\_content call.

**File: src/llm/google\_client.py**

Python

import os  
import logging  
import google.generativeai as genai  
from .base import BaseLLM  
from typing import Any

logger \= logging.getLogger(\_\_name\_\_)

class GoogleLLM(BaseLLM):  
    """Google LLM client for interacting with the Gemini API."""

    def \_\_init\_\_(self, api\_key: str \= None, model\_name: str \= "gemini-1.5-flash-latest"):  
        """  
        Initialize Google LLM client.

        Args:  
            api\_key: Google API Key. Defaults to GOOGLE\_API\_KEY env variable.  
            model\_name: The name of the model to use.  
        """  
        self.api\_key \= api\_key or os.getenv('GOOGLE\_API\_KEY')  
        if not self.api\_key:  
            raise ValueError("Google API key is not set. Please set the GOOGLE\_API\_KEY environment variable.")

        try:  
            genai.configure(api\_key=self.api\_key)  
            self.model \= genai.GenerativeModel(model\_name)  
            self.model\_name \= model\_name  
            logger.info(f"Initialized Google Gemini client with model: {self.model\_name}")  
        except Exception as e:  
            logger.error(f"Failed to configure Google Gemini client: {e}")  
            raise

    def generate(self, prompt: str, \*\*kwargs: Any) \-\> str:  
        """  
        Generate text using the configured Gemini model.

        Args:  
            prompt: Input prompt for the model.  
            \*\*kwargs: Additional parameters for the generation config (e.g., temperature).

        Returns:  
            Generated text response.

        Raises:  
            Exception: If generation fails.  
        """  
        try:  
            logger.debug(f"Generating with Google Gemini model {self.model\_name}")  
            \# Construct generation\_config from kwargs  
            generation\_config \= genai.types.GenerationConfig(\*\*kwargs) if kwargs else None

            response \= self.model.generate\_content(  
                prompt,  
                generation\_config=generation\_config  
            )

            \# Accessing the text from the response  
            if response.candidates and response.candidates\[0\].content.parts:  
                return response.candidates\[0\].content.parts\[0\].text  
            else:  
                \# Handle cases where the prompt might be blocked  
                logger.warning(f"Gemini response has no content. Prompt may have been blocked. Details: {response.prompt\_feedback}")  
                return f"\[Gemini Safety Block: {response.prompt\_feedback}\]"

        except Exception as e:  
            logger.error(f"Google Gemini text generation failed: {e}")  
            raise

### **4\. Create an LLM Provider Factory**

To easily switch between Ollama, OpenAI, and Google, you can create a factory function that reads the LLM\_PROVIDER environment variable and returns the correct client instance.

Create a new file **src/llm/factory.py**:

Python

\# src/llm/factory.py

import os  
import logging  
from .base import BaseLLM  
from .ollama\_client import OllamaLLM  
from .openai\_client import OpenAILLM  
from .google\_client import GoogleLLM

logger \= logging.getLogger(\_\_name\_\_)

def get\_llm\_client() \-\> BaseLLM:  
    """  
    Factory function to get the appropriate LLM client based on the environment variable.  
    """  
    provider \= os.getenv('LLM\_PROVIDER', 'ollama').lower()  
    logger.info(f"LLM\_PROVIDER set to '{provider}'. Initializing corresponding client.")

    if provider \== 'google':  
        return GoogleLLM()  
    elif provider \== 'openai':  
        \# Assuming you will implement OpenAILLM similarly  
        return OpenAILLM()  
    elif provider \== 'ollama':  
        return OllamaLLM()  
    else:  
        logger.warning(f"Unknown LLM\_PROVIDER '{provider}'. Defaulting to Ollama.")  
        return OllamaLLM()

### **5\. Update the Ingestion Pipeline**

Modify your main script, run\_ingestion.py, to use the new factory function. This removes the hardcoded OllamaLLM initialization.

**File: run\_ingestion.py**

Python

import logging  
from src.backend.graph\_ingestion\_service import GraphIngestionService  
from src.graph.neo4j\_client import Neo4jClient  
from src.llm.factory import get\_llm\_client \# \<--- IMPORT THE FACTORY

\# Configure logging  
logging.basicConfig(level=logging.INFO, format\='%(asctime)s \- %(levelname)s \- %(message)s')  
logger \= logging.getLogger(\_\_name\_\_)

def main():  
    """  
    Main function to run the GTD file ingestion pipeline.  
    """  
    logger.info("Starting GTD file ingestion pipeline...")  
    neo4j\_client \= None  
    try:  
        \# Initialize clients using the factory  
        logger.info("Initializing clients...")  
        neo4j\_client \= Neo4jClient()  
        llm\_client \= get\_llm\_client() \# \<--- USE THE FACTORY

        \# Health check for Ollama is now client-specific; can be removed or generalized  
        \# if hasattr(llm\_client, 'health\_check') and not llm\_client.health\_check():  
        \#     logger.error(f"{llm\_client.\_\_class\_\_.\_\_name\_\_} is not healthy.")  
        \#     return

        \# Initialize ingestion service  
        ingestion\_service \= GraphIngestionService(neo4j\_client, llm\_client) \# \<--- PASS THE CLIENT

        \# Run ingestion  
        gtd\_file \= "gtd.txt"  
        logger.info(f"Ingesting notes from '{gtd\_file}'...")  
        ingestion\_service.ingest\_gtd\_file(gtd\_file)

        logger.info("✅ Ingestion pipeline completed successfully\!")  
        logger.info("Check your Neo4j browser to see the updated graph.")

    except Exception as e:  
        logger.error(f"An error occurred during the ingestion pipeline: {e}", exc\_info=True)  
    finally:  
        if neo4j\_client:  
            neo4j\_client.close()  
            logger.info("Neo4j connection closed.")

if \_\_name\_\_ \== '\_\_main\_\_':  
    main()

### **6\. How to Use**

You can now switch between LLM providers by simply changing an environment variable in your .env file.

**To use Google Gemini:**

Bash

\# .env  
LLM\_PROVIDER=google  
GOOGLE\_API\_KEY="YOUR\_API\_KEY\_HERE"  
\# ... other vars

**To switch back to Ollama:**

Bash

\# .env  
LLM\_PROVIDER=ollama  
OLLAMA\_BASE\_URL=http://localhost:11434  
\# ... other vars

After setting the environment variable, run your ingestion script as usual:

Bash

python run\_ingestion.py

The application will automatically select and initialize the configured LLM client.

**Źródła**  
1\. [https://github.com/ssundell1/cruncher](https://github.com/ssundell1/cruncher)