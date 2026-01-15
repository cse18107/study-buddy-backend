from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.cloudinary_service import (
    upload_image_to_cloudinary,
    delete_image_from_cloudinary,
    get_optimized_image_url
)
from app.schemas.image import (
    ImageUploadResponse,
    ImageDeleteResponse,
    OptimizedImageUrlRequest,
    OptimizedImageUrlResponse
)
from typing import Optional

router = APIRouter()

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff"
]


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = "study_buddy"
):
    """
    Upload an image to Cloudinary.
    
    This endpoint:
    1. Accepts an image file
    2. Validates the file type
    3. Converts it to bytes
    4. Creates a signed upload to Cloudinary
    5. Returns the secure URL and metadata
    
    Args:
        file: The image file to upload (JPEG, PNG, GIF, WEBP, BMP, TIFF)
        folder: Optional folder name in Cloudinary (default: "study_buddy")
    
    Returns:
        ImageUploadResponse: Contains the secure URL and image metadata
    
    Raises:
        HTTPException: If file type is invalid or upload fails
    """
    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    try:
        # Read file bytes
        image_bytes = await file.read()
        
        # Validate file is not empty
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Upload to Cloudinary with signed upload
        result = upload_image_to_cloudinary(
            image_bytes=image_bytes,
            filename=file.filename or "unnamed",
            folder=folder
        )
        
        return ImageUploadResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.delete("/delete-image/{public_id:path}", response_model=ImageDeleteResponse)
async def delete_image(public_id: str):
    """
    Delete an image from Cloudinary using its public ID.
    
    Args:
        public_id: The public ID of the image (e.g., "study_buddy/image_20231220_153045")
    
    Returns:
        ImageDeleteResponse: Success status and message
    
    Raises:
        HTTPException: If deletion fails
    """
    try:
        result = delete_image_from_cloudinary(public_id)
        return ImageDeleteResponse(
            success=True,
            message="Image deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.post("/optimized-url", response_model=OptimizedImageUrlResponse)
async def get_optimized_url(request: OptimizedImageUrlRequest):
    """
    Generate an optimized image URL with transformations.
    
    Args:
        request: OptimizedImageUrlRequest containing public_id and transformation params
    
    Returns:
        OptimizedImageUrlResponse: The optimized image URL
    
    Raises:
        HTTPException: If URL generation fails
    """
    try:
        url = get_optimized_image_url(
            public_id=request.public_id,
            width=request.width,
            height=request.height,
            crop=request.crop
        )
        return OptimizedImageUrlResponse(url=url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate optimized URL: {str(e)}"
        )
