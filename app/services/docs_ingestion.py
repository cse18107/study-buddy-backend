from langchain_community.document_loaders import PyPDFLoader
from tempfile import NamedTemporaryFile
import os

from .splitter import split_documents
from .vector_store import store_embeddings

def ingest_document(file_bytes: bytes, filename: str, namespace: str) -> None:
    """
    Processes a single uploaded PDF file and stores it in the vector database.
    """
    # Create a temporary file to store the uploaded content
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # 1. Load the document
        print(f"Loading document: {filename}")
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # 2. Split the document into chunks
        chunked_documents = split_documents(documents)

        # 3. Store embeddings in the vector store
        store_embeddings(chunked_documents, namespace=namespace)
        print(f"Successfully ingested and processed {filename}")

    finally:
        # 4. Clean up the temporary file
        os.remove(tmp_path)