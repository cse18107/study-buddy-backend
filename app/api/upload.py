from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services import docs_ingestion

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF document for processing.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    try:
        file_bytes = await file.read()
        docs_ingestion.ingest_document(file_bytes, file.filename)
        return {"status": "success", "filename": file.filename, "message": "File processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")