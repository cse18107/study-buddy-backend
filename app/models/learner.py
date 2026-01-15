import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.classroom import Classroom

class Learner(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str = Field(min_length=6, max_length=72)
    
    classrooms: List["Classroom"] = Relationship(back_populates="learner")
