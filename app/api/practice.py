from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from uuid import UUID
from datetime import datetime, date, timedelta
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy import func
from app.core.database import get_session
from app.api.deps import get_current_learner
from app.models.learner import Learner
from app.models.practice import Practice
from app.schemas.practice import PracticeCreate, PracticeRead, PracticeUpdate
from app.services.practice_service import (
    create_practice, get_practices, get_practice_by_id,
    update_practice, delete_practice, get_practices_by_classroom_id
)
from app.services.classroom_service import get_classroom_by_id
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.source_service import get_source_by_classroom_and_document
from app.services.question_generator import generate_practice_questions
from app.models.enums import QuestionType

router = APIRouter(tags=["Practices"])

@router.post("/create", response_model=PracticeRead)
async def create(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    classroomId: UUID = Form(...),
    documentId: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    # 1. Verification
    classroom = get_classroom_by_id(classroomId, session)
    if not classroom or classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to add practice to this classroom")

    source = get_source_by_classroom_and_document(classroomId, documentId, session)
    if not source or not source.extractedHierarchy:
        raise HTTPException(status_code=404, detail="Source or hierarchy not found for this document")

    # 2. Upload Image
    try:
        file_bytes = await file.read()
        upload_result = upload_image_to_cloudinary(file_bytes, file.filename)
        file_url = upload_result.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    # 3. Create Practice
    practice_data = PracticeCreate(
        title=title,
        description=description,
        file=file_url,
        classroom_id=classroomId
    )
    # Mapping logic in service or manually here? Schema expects classroom_id usually if we use the model directly
    # But PracticeCreate defined in schema uses classroom_id (or updated to classroomId?)
    # Let's check schema updates. I updated PracticeCreate to Optional classroom_id.
    # We will instantiate Model effectively or use service.
    # Service expects Pydantic model. We created it above.
    practice = create_practice(practice_data, session)

    # 4. Generate Questions
    # This might take time. For now, running synchronously as requested "then... store... result"
    generate_practice_questions(practice.id, source.extractedHierarchy, documentId, session)
    
    # 5. Refresh to get questions populated? 
    # Or just return the practice info. The user asked for "response same way" (ordered questions)
    # So we probably need to fetch full details including questions.
    # The normal response_model=PracticeRead might not include questions unless we updated PracticeRead.
    # Let's check PracticeRead. It creates simple response.
    # We might need a custom response or rely on the Get API for full details.
    # "in final response you have to order the response data, where first we will have all the mcq..."
    # So I need to return a custom structure.
    
    # Let's fetch questions explicitly
    session.refresh(practice)
    return format_practice_response(practice)

def format_practice_response(practice: Practice):
    # Sort questions: MCQ, Short, Long
    questions = practice.questions
    mcq = [q for q in questions if q.type == QuestionType.Mcq]
    short = [q for q in questions if q.type == QuestionType.Short]
    long = [q for q in questions if q.type == QuestionType.Long]
    
    sorted_questions = mcq + short + long
    
    return {
        "id": practice.id,
        "title": practice.title,
        "description": practice.description,
        "file": practice.file,
        "classroomId": practice.classroom_id,
        "status": practice.status,
        "questions": sorted_questions
    }

@router.get("/classroom/{classroom_id}", response_model=list[PracticeRead])
def get_by_classroom(
    classroom_id: UUID,
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    # Verify classroom belongs to learner
    classroom = get_classroom_by_id(classroom_id, session)
    if not classroom or classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access practices for this classroom")
            
    practices = get_practices_by_classroom_id(classroom_id, session)
    
    result = []
    for practice in practices:
        total_marks = sum(q.assignedMarks for q in practice.questions)
        user_marks = sum((q.givenMarks or 0) for q in practice.questions)
        
        practice_read = PracticeRead.model_validate(practice.model_dump())
        practice_read.totalMarks = total_marks
        practice_read.userMarks = user_marks
        result.append(practice_read)
        
    return result

@router.get("/", response_model=list[PracticeRead])
def list_items(
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    all_items = get_practices(session)
    return [p for p in all_items if p.classroom and p.classroom.learner_id == current_learner.id]

@router.get("/{item_id}")
def get(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_practice_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Practice not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this practice")
    
    return format_practice_response(item)

@router.put("/{item_id}", response_model=PracticeRead)
def update(
    item_id: UUID, 
    data: PracticeUpdate, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_practice_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Practice not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this practice")

    if data.classroom_id:
         new_classroom = get_classroom_by_id(data.classroom_id, session)
         if not new_classroom or new_classroom.learner_id != current_learner.id:
             raise HTTPException(status_code=403, detail="Not authorized to move practice to this classroom")

    return update_practice(item_id, data, session)

@router.delete("/{item_id}")
def delete(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_practice_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Practice not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this practice")
    
    success = delete_practice(item_id, session)
    return {"status": "deleted"}

@router.get("/stats/daily")
def get_daily_stats(
    start_date: date,
    end_date: date,
    classroom_id: Optional[UUID] = None,
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    from app.models.classroom import Classroom
    
    # Query for practice counts by date for the current learner
    query = (
        select(func.date(Practice.created_at).label("practice_date"), func.count(Practice.id).label("count"))
        .join(Classroom, Practice.classroom_id == Classroom.id)
        .where(Classroom.learner_id == current_learner.id)
        .where(Practice.created_at >= datetime.combine(start_date, datetime.min.time()))
        .where(Practice.created_at <= datetime.combine(end_date, datetime.max.time()))
    )

    if classroom_id:
        query = query.where(Practice.classroom_id == classroom_id)

    query = query.group_by(func.date(Practice.created_at))
    
    results = session.exec(query).all()
    
    final_stats = [
        {"date": str(r[0]), "count": r[1]} 
        for r in results
    ]
    
    return final_stats
