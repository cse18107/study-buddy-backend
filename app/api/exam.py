from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from uuid import UUID
from datetime import datetime, date, timedelta
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy import func
from app.core.database import get_session
from app.api.deps import get_current_learner
from app.models.learner import Learner
from app.models.exam import Exam
from app.models.enums import QuestionDifficulty, QuestionType
from app.schemas.exam import ExamCreate, ExamRead, ExamUpdate
from app.services.exam_service import (
    create_exam, get_exams, get_exam_by_id,
    update_exam, delete_exam, get_exams_by_classroom_id
)
from app.services.classroom_service import get_classroom_by_id
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.source_service import get_source_by_classroom_and_document
from app.services.question_generator import generate_exam_questions

router = APIRouter(tags=["Exams"])

@router.post("/create", response_model=ExamRead)
async def create(
    title: str = Form(...),
    difficulty: QuestionDifficulty = Form(...),
    date: datetime = Form(...),
    description: Optional[str] = Form(None),
    classroomId: UUID = Form(...),
    documentId: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    classroom = get_classroom_by_id(classroomId, session)
    if not classroom or classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to add exam to this classroom")
    print(classroomId, documentId)
    source = get_source_by_classroom_and_document(classroomId, documentId, session)
    if not source or not source.extractedHierarchy:
        raise HTTPException(status_code=404, detail="Source or hierarchy not found for this document")

    try:
        file_bytes = await file.read()
        upload_result = upload_image_to_cloudinary(file_bytes, file.filename)
        file_url = upload_result.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    exam_data = ExamCreate(
        title=title,
        description=description,
        file=file_url,
        classroom_id=classroomId,
        difficulty=difficulty,
        date=date
    )
    exam = create_exam(exam_data, session)

    generate_exam_questions(exam.id, source.extractedHierarchy, documentId, session)
    
    session.refresh(exam)
    return format_exam_response(exam)

def format_exam_response(exam: Exam):
    questions = exam.questions
    mcq = [q for q in questions if q.type == QuestionType.Mcq]
    short = [q for q in questions if q.type == QuestionType.Short]
    long = [q for q in questions if q.type == QuestionType.Long]
    
    sorted_questions = mcq + short + long
    
    return {
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "file": exam.file,
        "classroomId": exam.classroom_id,
        "difficulty": exam.difficulty,
        "date": exam.date,
        "status": exam.status,
        "questions": sorted_questions
    }

@router.get("/", response_model=list[ExamRead])
def list_items(
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    all_items = get_exams(session)
    return [e for e in all_items if e.classroom and e.classroom.learner_id == current_learner.id]

@router.get("/classroom/{classroom_id}", response_model=list[ExamRead])
def get_by_classroom(
    classroom_id: UUID,
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    # Verify classroom belongs to learner
    classroom = get_classroom_by_id(classroom_id, session)
    if not classroom or classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access exams for this classroom")
            
    exams = get_exams_by_classroom_id(classroom_id, session)
    
    result = []
    for exam in exams:
        total_marks = sum(q.assignedMarks for q in exam.questions)
        user_marks = sum((q.givenMarks or 0) for q in exam.questions)
        
        exam_read = ExamRead.model_validate(exam.model_dump())
        exam_read.totalMarks = total_marks
        exam_read.userMarks = user_marks
        result.append(exam_read)
        
    return result

@router.get("/{item_id}")
def get(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_exam_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Exam not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this exam")
    
    return format_exam_response(item)

@router.put("/{item_id}", response_model=ExamRead)
def update(
    item_id: UUID, 
    data: ExamUpdate, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_exam_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Exam not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exam")

    if data.classroom_id:
         new_classroom = get_classroom_by_id(data.classroom_id, session)
         if not new_classroom or new_classroom.learner_id != current_learner.id:
             raise HTTPException(status_code=403, detail="Not authorized to move exam to this classroom")

    return update_exam(item_id, data, session)

@router.delete("/{item_id}")
def delete(
    item_id: UUID, 
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    item = get_exam_by_id(item_id, session)
    if not item:
        raise HTTPException(404, "Exam not found")
    if not item.classroom or item.classroom.learner_id != current_learner.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this exam")
    
    success = delete_exam(item_id, session)
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
    
    # Query for exam counts by date for the current learner
    query = (
        select(func.date(Exam.date).label("exam_date"), func.count(Exam.id).label("count"))
        .join(Classroom, Exam.classroom_id == Classroom.id)
        .where(Classroom.learner_id == current_learner.id)
        .where(Exam.date >= datetime.combine(start_date, datetime.min.time()))
        .where(Exam.date <= datetime.combine(end_date, datetime.max.time()))
    )
    
    if classroom_id:
        query = query.where(Exam.classroom_id == classroom_id)
        
    query = query.group_by(func.date(Exam.date))
    
    results = session.exec(query).all()
    
    final_stats = [
        {"date": str(r[0]), "count": r[1]} 
        for r in results
    ]
    
    return final_stats

@router.get("/stats/performance")
def get_exam_performance(
    start_date: date,
    end_date: date,
    classroom_id: Optional[UUID] = None,
    session: Session = Depends(get_session),
    current_learner: Learner = Depends(get_current_learner)
):
    from app.models.classroom import Classroom
    from app.models.question import Question
    
    # Query for exams and their total marks
    # We join Question to calculate assigned vs given marks
    query = (
        select(
            Exam.id,
            Exam.date,
            func.sum(Question.assignedMarks).label("total_assigned"),
            func.sum(Question.givenMarks).label("total_given")
        )
        .join(Classroom, Exam.classroom_id == Classroom.id)
        .join(Question, Exam.id == Question.exam_id)
        .where(Classroom.learner_id == current_learner.id)
        .where(Exam.date >= datetime.combine(start_date, datetime.min.time()))
        .where(Exam.date <= datetime.combine(end_date, datetime.max.time()))
    )
    
    if classroom_id:
        query = query.where(Exam.classroom_id == classroom_id)
        
    query = query.group_by(Exam.id, Exam.date).order_by(Exam.date.desc())
    
    results = session.exec(query).all()
    
    performance_data = []
    for r in results:
        exam_id, exam_date, total_assigned, total_given = r
        
        # Avoid division by zero
        score_percent = 0
        if total_assigned and total_assigned > 0:
            score_percent = round((total_given or 0) / total_assigned * 100, 2)
            
        performance_data.append({
            "name": exam_date.strftime("%Y-%m-%d"),
            "score": score_percent
        })
        
    return performance_data
