from langchain_pinecone import PineconeVectorStore
from langchain_core.vectorstores import VectorStoreRetriever
from typing import List
from pinecone import Pinecone

from langchain_core.documents import Document

from app.core.config import settings
from app.core.embeddings import embeddings_model

def store_embeddings(documents: List[Document], namespace: str = None) -> None:
    """
    Stores document embeddings in the Pinecone index.
    This function will add new documents to the existing index.
    """
   
    print(f"Adding {len(documents)} documents to vector store '{settings.PINECONE_INDEX_NAME} with API key '...")
    PineconeVectorStore.from_documents(
        documents,
        embeddings_model,
        index_name=settings.PINECONE_INDEX_NAME,
        namespace=namespace
    )
    print("Embeddings stored successfully.")

def get_retriever(namespace: str = None) -> VectorStoreRetriever:
    """
    Connects to the existing Pinecone index and returns a retriever.
    """
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings_model,
        namespace=namespace
    )
    return docsearch.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 100, "fetch_k": 100, "lambda_mult": 0.3} # Retrieve top 100 results
    )