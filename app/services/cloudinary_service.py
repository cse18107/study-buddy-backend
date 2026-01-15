import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from app.core.config import settings
import base64
from typing import Optional
from datetime import datetime

# Initialize Cloudinary configuration
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


def upload_image_to_cloudinary(
    image_bytes: bytes,
    filename: str,
    folder: str = "study_buddy"
) -> dict:
    """
    Upload an image to Cloudinary with signed upload.
    
    Args:
        image_bytes: The image file in bytes
        filename: Original filename
        folder: Cloudinary folder to upload to (default: "study_buddy")
    
    Returns:
        dict: Contains the secure_url and public_id of the uploaded image
    
    Raises:
        Exception: If upload fails
    """
    try:
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_without_ext = filename.rsplit('.', 1)[0]
        public_id = f"{folder}/{name_without_ext}_{timestamp}"
        
        # Upload the image using signed upload
        upload_result = cloudinary.uploader.upload(
            image_bytes,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
            folder=folder,
            invalidate=True
        )
        
        return {
            "success": True,
            "url": upload_result.get('secure_url'),
            "public_id": upload_result.get('public_id'),
            "format": upload_result.get('format'),
            "width": upload_result.get('width'),
            "height": upload_result.get('height'),
            "bytes": upload_result.get('bytes'),
            "created_at": upload_result.get('created_at')
        }
    
    except Exception as e:
        raise Exception(f"Failed to upload image to Cloudinary: {str(e)}")


def delete_image_from_cloudinary(public_id: str) -> dict:
    """
    Delete an image from Cloudinary using its public_id.
    
    Args:
        public_id: The public ID of the image to delete
    
    Returns:
        dict: Result of the deletion operation
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise Exception(f"Failed to delete image from Cloudinary: {str(e)}")


def get_optimized_image_url(
    public_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    crop: str = "fill"
) -> str:
    """
    Generate an optimized image URL with transformations.
    
    Args:
        public_id: The public ID of the image
        width: Desired width
        height: Desired height
        crop: Crop mode (fill, fit, scale, etc.)
    
    Returns:
        str: Optimized image URL
    """
    try:
        transformation = []
        
        if width:
            transformation.append({"width": width})
        if height:
            transformation.append({"height": height})
        if width or height:
            transformation.append({"crop": crop})
        
        transformation.append({"quality": "auto"})
        transformation.append({"fetch_format": "auto"})
        
        url, _ = cloudinary_url(
            public_id,
            transformation=transformation,
            secure=True
        )
        
        return url
    except Exception as e:
        raise Exception(f"Failed to generate optimized URL: {str(e)}")


def upload_pdf_to_cloudinary(
    pdf_bytes: bytes,
    filename: str,
    folder: str = "study_buddy/pdfs"
) -> dict:
    """
    Upload a PDF file to Cloudinary with signed upload.
    
    Args:
        pdf_bytes: The PDF file in bytes
        filename: Original filename
        folder: Cloudinary folder to upload to (default: "study_buddy/pdfs")
    
    Returns:
        dict: Contains the secure_url and public_id of the uploaded PDF
    
    Raises:
        Exception: If upload fails
    """
    try:
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_without_ext = filename.rsplit('.', 1)[0]
        public_id = f"{folder}/{name_without_ext}_{timestamp}"
        
        # Upload the PDF using signed upload (raw resource type for PDFs)
        upload_result = cloudinary.uploader.upload(
            pdf_bytes,
            public_id=public_id,
            overwrite=True,
            resource_type="raw",  # Use 'raw' for non-image files like PDFs
            folder=folder,
            invalidate=True
        )
        
        return {
            "success": True,
            "url": upload_result.get('secure_url'),
            "public_id": upload_result.get('public_id'),
            "format": upload_result.get('format'),
            "bytes": upload_result.get('bytes'),
            "created_at": upload_result.get('created_at')
        }
    
    except Exception as e:
        raise Exception(f"Failed to upload PDF to Cloudinary: {str(e)}")
