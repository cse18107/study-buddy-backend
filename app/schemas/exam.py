from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import QuestionDifficulty, Status

class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None
    difficulty: QuestionDifficulty
    date: datetime

class ExamRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None
    difficulty: QuestionDifficulty
    date: datetime
    status: Status
    totalMarks: float = 0
    userMarks: float = 0

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None
    difficulty: Optional[QuestionDifficulty] = None
    date: Optional[datetime] = None
    status: Optional[Status] = None
