from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.core.database import get_session
from pydantic import BaseModel
from typing import Optional
from app.services import rag_pipeline
from app.services.source_service import get_source_by_id, update_source
from app.schemas.source import SourceUpdate
from app.models.prompt_enums import PromptType

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    namespace: Optional[str] = None
    source_id: Optional[UUID] = None
    prompt_type: PromptType = PromptType.HTML_EXPLANATION

class QueryResponse(BaseModel):
    answer: str

@router.post("/generate-content", response_model=QueryResponse)
async def query_rag(request: QueryRequest, session: Session = Depends(get_session)):
    """
    Endpoint to ask a question to the RAG pipeline.
    Optionally, if source_id is provided, the answer is saved to that source's extractedHierarchy.
    
    The prompt_type parameter determines which prompt template to use:
    - "html_explanation": Generates detailed HTML-formatted educational content (default)
    - "hierarchy_extraction": Extracts hierarchical structure as JSON from documents
    """
    try:
        answer = rag_pipeline.ask_question(request.question, namespace=request.namespace, prompt_type=request.prompt_type)
        
        # if request.source_id:
        #     source = get_source_by_id(request.source_id, session)
        #     if source:
        #         update_data = SourceUpdate(extractedHierarchy=answer)
        #         update_source(request.source_id, update_data, session)
        #     else:
        #          raise HTTPException(status_code=404, detail="Source not found")
                 
        return QueryResponse(answer=answer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")