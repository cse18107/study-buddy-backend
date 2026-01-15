from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import json
from typing import Optional
from .vector_store import get_retriever
from app.core.llm import llm
from .prompts import build_prompt, build_prompt_for_heirarchy_doc
from app.models.prompt_enums import PromptType

def format_docs(docs):
    """Helper function to format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)

def create_rag_chain(namespace: Optional[str] = None, prompt_type: PromptType = PromptType.HTML_EXPLANATION):
    """
    Creates and returns the RAG chain.
    
    Args:
        namespace: The namespace for the vector store retriever
        prompt_type: The type of prompt to use (from PromptType enum)
    """
    retriever = get_retriever(namespace=namespace)
    
    # Select the appropriate prompt based on prompt_type
    if prompt_type == PromptType.HIERARCHY_EXTRACTION:
        prompt = build_prompt_for_heirarchy_doc()
    elif prompt_type == PromptType.HTML_EXPLANATION:
        prompt = build_prompt()
    else:
        raise ValueError(f"Unsupported prompt type: {prompt_type}")
    
    rag_chain = (
        {
            "context": itemgetter("input") | retriever | format_docs,
            "input": RunnablePassthrough(),
        }
        | prompt
        | llm
    )
    return rag_chain

def ask_question(question: str, namespace: Optional[str] = None, prompt_type: PromptType = PromptType.HTML_EXPLANATION) -> str:
    """
    Invokes the RAG chain with a question and returns the answer.
    
    Args:
        question: The question to ask
        namespace: The namespace for the vector store retriever
        prompt_type: The type of prompt to use (from PromptType enum)
    """
    rag_chain = create_rag_chain(namespace=namespace, prompt_type=prompt_type)
    response = rag_chain.invoke({"input": question})
    return response.content