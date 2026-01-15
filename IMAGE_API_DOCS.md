# Image Upload API Documentation

## Overview
This API provides endpoints to upload images to Cloudinary with signed uploads, delete images, and generate optimized image URLs.

## Setup

### 1. Install Dependencies
```bash
pip install cloudinary
```

### 2. Configure Cloudinary Credentials
Add the following to your `.env` file:
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

To get your Cloudinary credentials:
1. Sign up at [https://cloudinary.com](https://cloudinary.com)
2. Go to your Dashboard
3. Copy the Cloud Name, API Key, and API Secret

## API Endpoints

### 1. Upload Image

**Endpoint:** `POST /api/images/upload-image`

**Description:** Upload an image file to Cloudinary with signed upload.

**Supported formats:** JPEG, PNG, GIF, WEBP, BMP, TIFF

**Parameters:**
- `file` (required): Image file to upload
- `folder` (optional): Cloudinary folder name (default: "study_buddy")

**Response:**
```json
{
  "success": true,
  "url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/study_buddy/filename_20231220_153045.jpg",
  "public_id": "study_buddy/filename_20231220_153045",
  "format": "jpg",
  "width": 1920,
  "height": 1080,
  "bytes": 245678,
  "created_at": "2023-12-20T15:30:45Z",
  "message": "Image uploaded successfully"
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/images/upload-image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "folder=study_buddy"
```

### 2. Delete Image

**Endpoint:** `DELETE /api/images/delete-image/{public_id}`

**Description:** Delete an image from Cloudinary using its public ID.

**Parameters:**
- `public_id` (required): The public ID of the image (e.g., "study_buddy/image_20231220_153045")

**Response:**
```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/images/delete-image/study_buddy/image_20231220_153045"
```

### 3. Get Optimized Image URL

**Endpoint:** `POST /api/images/optimized-url`

**Description:** Generate an optimized and transformed image URL.

**Request Body:**
```json
{
  "public_id": "study_buddy/image_20231220_153045",
  "width": 800,
  "height": 600,
  "crop": "fill"
}
```

**Response:**
```json
{
  "url": "https://res.cloudinary.com/your-cloud/image/upload/w_800,h_600,c_fill,q_auto,f_auto/study_buddy/image_20231220_153045"
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/images/optimized-url" \
  -H "Content-Type: application/json" \
  -d '{
    "public_id": "study_buddy/image_20231220_153045",
    "width": 800,
    "height": 600,
    "crop": "fill"
  }'
```

## How It Works

### Upload Process
1. **Client sends image**: The API receives the image file
2. **Validation**: Checks if the file type is allowed
3. **Convert to bytes**: Reads the file content as bytes
4. **Signed upload**: Uses Cloudinary's signed upload API for security
5. **Return URL**: Returns the secure HTTPS URL of the uploaded image

### Security Features
- **Signed uploads**: All uploads are signed using your API secret
- **File type validation**: Only allows specified image formats
- **Secure URLs**: All returned URLs use HTTPS
- **Auto-format**: Cloudinary automatically optimizes the format
- **Auto-quality**: Automatically adjusts quality for best performance

## Testing

### Using Swagger UI
1. Start your server: `uvicorn app.main:app --reload`
2. Navigate to: `http://127.0.0.1:8000/docs`
3. Find the "Images" section
4. Test the `/api/images/upload-image` endpoint

### Using cURL
```bash
# Upload an image
curl -X POST "http://127.0.0.1:8000/api/images/upload-image" \
  -F "file=@test-image.jpg"

# The response will contain the URL and public_id
# Use the public_id to delete the image
curl -X DELETE "http://127.0.0.1:8000/api/images/delete-image/study_buddy/test-image_20231220_153045"
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file type, empty file)
- `500`: Server error (Cloudinary upload failed)

## Notes

- Images are automatically timestamped to prevent naming conflicts
- The `folder` parameter helps organize images in Cloudinary
- All uploads use the `secure` flag for HTTPS URLs
- Images are uploaded with `auto` format and quality for optimization
