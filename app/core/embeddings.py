from langchain_openai import OpenAIEmbeddings
from .config import settings

def get_embeddings_model():
    """Initializes and returns the OpenAI embeddings model."""
    return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

# Create a singleton instance to be used across the application
embeddings_model = get_embeddings_model()