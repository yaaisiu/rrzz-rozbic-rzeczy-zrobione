import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.openai_client import OpenAILLM

@pytest.fixture
def openai_client():
    """Fixture for OpenAILLM client."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test_api_key",
        "OPENAI_MODEL_NAME": "gpt-4o"
    }):
        return OpenAILLM()

def test_openai_init_with_api_key(openai_client):
    """Test if the OpenAI client initializes correctly with an API key."""
    assert openai_client.api_key == "test_api_key"
    assert openai_client.model_name == "gpt-4o"
    assert openai_client.client is not None

def test_openai_init_no_api_key():
    """Test if ValueError is raised when no API key is provided."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        with pytest.raises(ValueError, match="OpenAI API key is not set"):
            OpenAILLM()

@patch('openai.resources.chat.completions.Completions.create')
def test_openai_generate_successful(mock_create, openai_client):
    """Test a successful text generation call."""
    # Create a mock response object
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a test response."
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    mock_create.return_value = mock_completion

    prompt = "Hello, world!"
    response = openai_client.generate(prompt, temperature=0.7)

    mock_create.assert_called_once_with(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides structured data."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    assert response == "This is a test response."

@patch('openai.resources.chat.completions.Completions.create')
def test_openai_generate_empty_response(mock_create, openai_client):
    """Test the case where the API returns an empty response."""
    # Create a mock response object with no content
    mock_choice = MagicMock()
    mock_choice.message.content = ""
    
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_create.return_value = mock_completion

    response = openai_client.generate("A prompt that yields no response")
    assert response == "[No response from OpenAI]"

@patch('openai.resources.chat.completions.Completions.create')
def test_openai_generate_api_error(mock_create, openai_client):
    """Test how the client handles an API error during generation."""
    mock_create.side_effect = Exception("API connection failed")

    with pytest.raises(Exception, match="API connection failed"):
        openai_client.generate("A prompt that causes an error") 