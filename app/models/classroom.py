import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.learner import Learner
    from app.models.source import Source
    from app.models.practice import Practice
    from app.models.exam import Exam

class Classroom(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    classroomName: str
    subject: str
    
    learner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="learner.id")
    learner: Optional["Learner"] = Relationship(back_populates="classrooms")

    sources: List["Source"] = Relationship(back_populates="classroom")
    practices: List["Practice"] = Relationship(back_populates="classroom")
    exams: List["Exam"] = Relationship(back_populates="classroom")
