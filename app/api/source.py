import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_learner
from app.models.learner import Learner
from app.schemas.source import SourceCreate, SourceRead, SourceUpdate, SourceProcessRequest
from app.services.source_service import (
    create_source, get_sources, get_source_by_id,
    update_source, delete_source, get_source_by_classroom_and_document
)
from app.services.content_generator import generate_html_content
from app.services.classroom_service import get_classroom_by_id

router = APIRouter(tags=["Sources"])

@router.post("/", response_model=SourceRead)
def create(
    item: SourceCreate, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    if item.classroomId:
        classroom = get_classroom_by_id(item.classroomId, session)
        if not classroom or classroom.learner_id != current_learner.id:
            raise HTTPException(status_code=403, detail="Not authorized to add source to this classroom")
    return create_source(item, session)

@router.post("/generate-content")
def generate_content(
    data: SourceProcessRequest,
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    """
    Perform a bunch of operations on a source given classroomId and documentId.
    """
    classroom = get_classroom_by_id(data.classroomId, session)
    if not classroom or classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this classroom")

    source = get_source_by_classroom_and_document(data.classroomId, data.documentId, session)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    if not source.extractedHierarchy:
         # Handle case where hierarchy is missing. 
         # The user/n8n logic assumes it exists.
         return {"status": "error", "message": "No extracted hierarchy found in source"}

    generated_html, updated_hierarchy = generate_html_content(source.extractedHierarchy, data.documentId)
    
    # Store in source
    source.htmlContent = generated_html
    # Store updated hierarchy back as JSON string if it was a string, or as object if SQLModel handles it
    # Given model says Optional[str] = None
    if isinstance(updated_hierarchy, (list, dict)):
        source.extractedHierarchy = json.dumps(updated_hierarchy)
    else:
        source.extractedHierarchy = updated_hierarchy

    session.add(source)
    session.commit()
    session.refresh(source)

    return {"status": "success", "data": generated_html}

@router.get("/", response_model=list[SourceRead])
def list_items(
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    all_sources = get_sources(session)
    # This requires Source to have classroom loaded or accessible. 
    # Since we defined relationship in pure SQLModel, accessing .classroom might trigger lazy load if session is active.
    # However, filtering in python:
    # Map Source objects to SourceRead explicitly to handle schema field naming (classroomId vs classroom_id)
    results = []
    for s in all_sources:
        if s.classroom and s.classroom.learner_id == current_learner.id:
            # We explicitly set classroomId because source model has classroom_id
            s_dict = s.model_dump()
            s_dict['classroomId'] = s.classroom_id
            results.append(SourceRead(**s_dict))
    return results

@router.get("/{item_id}", response_model=SourceRead)
def get(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_source_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Source not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
         raise HTTPException(status_code=403, detail="Not authorized to access this source")
    
    # Map for response
    s_dict = item.model_dump()
    s_dict['classroomId'] = item.classroom_id
    return SourceRead(**s_dict)

@router.put("/{item_id}", response_model=SourceRead)
def update(
    item_id: UUID, 
    data: SourceUpdate, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_source_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Source not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
         raise HTTPException(status_code=403, detail="Not authorized to update this source")
    
    if data.classroomId:
         new_classroom = get_classroom_by_id(data.classroomId, session)
         if not new_classroom or new_classroom.learner_id != current_learner.id:
             raise HTTPException(status_code=403, detail="Not authorized to move source to this classroom")

    result = update_source(item_id, data, session)
    if result:
        s_dict = result.model_dump()
        s_dict['classroomId'] = result.classroom_id
        return SourceRead(**s_dict)
    return result

@router.delete("/{item_id}")
def delete(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_source_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Source not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
         raise HTTPException(status_code=403, detail="Not authorized to delete this source")
    
    success = delete_source(item_id, session)
    return {"status": "deleted"}
