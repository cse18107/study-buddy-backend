import uuid
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.classroom import Classroom
from app.models.enums import Status

if TYPE_CHECKING:
    from app.models.question import Question

class Practice(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    classroom_id: Optional[uuid.UUID] = Field(default=None, foreign_key="classroom.id")
    classroom: Optional[Classroom] = Relationship(back_populates="practices")
    
    questions: List["Question"] = Relationship(back_populates="practice")
    status: Status = Field(default=Status.Created)
