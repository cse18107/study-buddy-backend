from pydantic import BaseModel
from typing import Optional


class ImageUploadResponse(BaseModel):
    """Response model for image upload"""
    success: bool
    url: str
    public_id: str
    format: str
    width: int
    height: int
    bytes: int
    created_at: str
    message: str = "Image uploaded successfully"


class ImageDeleteResponse(BaseModel):
    """Response model for image deletion"""
    success: bool
    message: str


class OptimizedImageUrlRequest(BaseModel):
    """Request model for getting optimized image URL"""
    public_id: str
    width: Optional[int] = None
    height: Optional[int] = None
    crop: str = "fill"


class OptimizedImageUrlResponse(BaseModel):
    """Response model for optimized image URL"""
    url: str
