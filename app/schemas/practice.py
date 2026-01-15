from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.models.enums import Status

class PracticeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None

class PracticeRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None
    status: Status
    totalMarks: float = 0
    userMarks: float = 0

class PracticeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file: Optional[str] = None
    classroom_id: Optional[UUID] = None
    status: Optional[Status] = None
