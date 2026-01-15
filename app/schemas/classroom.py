from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.schemas.source import SourceRead
from app.schemas.practice import PracticeRead
from app.schemas.exam import ExamRead

class ClassroomCreate(BaseModel):
    classroomName: str
    subject: str
    learner_id: Optional[UUID] = None

class ClassroomRead(BaseModel):
    id: UUID
    classroomName: str
    subject: str
    learner_id: Optional[UUID] = None
    sources: List[SourceRead] = []

class ClassroomReadWithDetails(ClassroomRead):
    sources: List[SourceRead] = []
    practices: List[PracticeRead] = []
    exams: List[ExamRead] = []

class ClassroomUpdate(BaseModel):
    classroomName: Optional[str] = None
    subject: Optional[str] = None
    learner_id: Optional[UUID] = None
