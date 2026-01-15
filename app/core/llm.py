from langchain_openai import ChatOpenAI
from .config import settings

def get_llm():
    """Initializes and returns the ChatOpenAI model."""
    return ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY)

# Create a singleton instance
llm = get_llm()