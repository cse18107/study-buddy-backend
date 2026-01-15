from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.models.enums import SourceType

class SourceCreate(BaseModel):
    sourceType: SourceType
    extractedHierarchy: Optional[str] = None
    htmlContent: Optional[str] = None
    link: Optional[str] = None
    document: Optional[str] = None
    classroomId: Optional[UUID] = None

class SourceRead(BaseModel):
    id: UUID
    sourceType: SourceType
    extractedHierarchy: Optional[str] = None
    htmlContent: Optional[str] = None
    link: Optional[str] = None
    document: Optional[str] = None
    classroomId: Optional[UUID] = None

class SourceUpdate(BaseModel):
    sourceType: Optional[SourceType] = None
    extractedHierarchy: Optional[str] = None
    htmlContent: Optional[str] = None
    link: Optional[str] = None
    document: Optional[str] = None
    classroomId: Optional[UUID] = None

class SourceProcessRequest(BaseModel):
    classroomId: UUID
    documentId: str
