from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session
from app.core.database import get_session
from app.api.deps import get_current_learner
from app.models.learner import Learner
from app.schemas.classroom import ClassroomCreate, ClassroomRead, ClassroomUpdate, ClassroomReadWithDetails
from app.services.classroom_service import (
    create_classroom, get_classrooms, get_classroom_by_id,
    update_classroom, delete_classroom
)

router = APIRouter(tags=["Classrooms"])

@router.post("/", response_model=ClassroomRead)
def create(
    classroomName: str = Form(...),
    subject: str = Form(...),
    pdf_file: UploadFile = File(...),
    # image_file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    # Create ClassroomCreate object from form data
    item = ClassroomCreate(classroomName=classroomName, subject=subject, learner_id=current_learner.id)
    
    # Read PDF content
    pdf_content = pdf_file.file.read()
    
    # Call service
    return create_classroom(item, session, pdf_file=pdf_content, pdf_filename=pdf_file.filename)

@router.get("/", response_model=list[ClassroomRead])
def list_items(
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    # Filter by user
    # Note: Service generic get_classrooms returns all. We should filter here or update service.
    # For simplicity, filtering in memory here, but better to filter in DB.
    # Let's filter in memory since we didn't update service yet.
    all_classrooms = get_classrooms(session)
    return [c for c in all_classrooms if c.learner_id == current_learner.id]

@router.get("/{item_id}", response_model=ClassroomReadWithDetails)
def get(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_classroom_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Classroom not found")
    if item.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this classroom")
    return item

@router.put("/{item_id}", response_model=ClassroomRead)
def update(
    item_id: UUID, 
    data: ClassroomUpdate, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_classroom_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Classroom not found")
    if item.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this classroom")
        
    updated_item = update_classroom(item_id, data, session)
    return updated_item

@router.delete("/{item_id}")
def delete(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_classroom_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Classroom not found")
    if item.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this classroom")
        
    success = delete_classroom(item_id, session)
    return {"status": "deleted"}
