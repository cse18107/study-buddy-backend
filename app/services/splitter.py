from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

def split_documents(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 50) -> List[Document]:
    """
    Splits a list of documents into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunked_docs = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunked_docs)} chunks.")
    return chunked_docs