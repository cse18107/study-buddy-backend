import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.classroom import Classroom
from app.models.enums import QuestionDifficulty, Status

if TYPE_CHECKING:
    from app.models.question import Question

class Exam(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[uuid.UUID] = Field(default=None, foreign_key="classroom.id")
    classroom: Optional[Classroom] = Relationship(back_populates="exams")
    
    questions: List["Question"] = Relationship(back_populates="exam")
    
    difficulty: QuestionDifficulty
    date: datetime
    status: Status = Field(default=Status.Created)
