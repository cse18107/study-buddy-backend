import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from app.models.enums import QuestionType, QuestionDifficulty
from app.models.practice import Practice
from app.models.exam import Exam

class Question(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: QuestionType
    question: str
    options: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    answer: str
    assignedMarks: float
    givenMarks: Optional[float] = None
    learnersAnswer: Optional[str] = None
    difficulty: QuestionDifficulty

    practice_id: Optional[uuid.UUID] = Field(default=None, foreign_key="practice.id")
    practice: Optional[Practice] = Relationship(back_populates="questions")

    exam_id: Optional[uuid.UUID] = Field(default=None, foreign_key="exam.id")
    exam: Optional[Exam] = Relationship(back_populates="questions")
