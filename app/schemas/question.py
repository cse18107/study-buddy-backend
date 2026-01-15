from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from app.models.enums import QuestionType, QuestionDifficulty

class QuestionCreate(BaseModel):
    type: QuestionType
    question: str
    options: List[str] = []
    answer: str
    assignedMarks: float
    givenMarks: Optional[float] = None
    difficulty: QuestionDifficulty
    practice_id: Optional[UUID] = None
    exam_id: Optional[UUID] = None

class QuestionRead(BaseModel):
    id: UUID
    type: QuestionType
    question: str
    options: List[str]
    answer: str
    assignedMarks: float
    givenMarks: Optional[float] = None
    learnersAnswer: Optional[str] = None
    difficulty: QuestionDifficulty
    practice_id: Optional[UUID] = None
    exam_id: Optional[UUID] = None

class QuestionUpdate(BaseModel):
    type: Optional[QuestionType] = None
    question: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    assignedMarks: Optional[float] = None
    givenMarks: Optional[float] = None
    learnersAnswer: Optional[str] = None
    difficulty: Optional[QuestionDifficulty] = None
    practice_id: Optional[UUID] = None
    exam_id: Optional[UUID] = None
