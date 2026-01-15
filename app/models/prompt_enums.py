from enum import Enum

class PromptType(str, Enum):
    """Enum for different prompt types available in the RAG pipeline."""
    HTML_EXPLANATION = "html_explanation"  # For detailed HTML-formatted educational content
    HIERARCHY_EXTRACTION = "hierarchy_extraction"  # For extracting hierarchical document structure
    CONTENT_GENERATION_HTML = "content_generation_html" # For generating HTML content from hierarchy items
