from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class LearnerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)

class LearnerRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr

class LearnerUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
