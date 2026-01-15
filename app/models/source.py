import uuid
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import SourceType

if TYPE_CHECKING:
    from app.models.classroom import Classroom

class Source(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sourceType: SourceType
    extractedHierarchy: Optional[str] = None
    htmlContent: Optional[str] = None
    link: Optional[str] = None # File path or content identifier
    document: Optional[str] = None

    classroom_id: Optional[uuid.UUID] = Field(default=None, foreign_key="classroom.id")
    classroom: Optional["Classroom"] = Relationship(back_populates="sources")
