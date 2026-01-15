from uuid import UUID
from sqlmodel import Session, select
from app.models.classroom import Classroom
from app.models.source import Source
from app.models.enums import SourceType
from app.services.docs_ingestion import ingest_document
import uuid
from app.services.rag_pipeline import ask_question
from app.models.prompt_enums import PromptType
from app.services.cloudinary_service import upload_pdf_to_cloudinary

def create_classroom(data, session: Session, pdf_file: bytes = None, pdf_filename: str = None):
    obj = Classroom.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    
    if pdf_file and pdf_filename:
        # Upload PDF to Cloudinary first
        pdf_link = None
        try:
            cloudinary_result = upload_pdf_to_cloudinary(pdf_file, pdf_filename)
            pdf_link = cloudinary_result.get('url')
            print(f"PDF uploaded to Cloudinary: {pdf_link}")
        except Exception as e:
            print(f"Error uploading PDF to Cloudinary: {str(e)}")
            # Continue with classroom creation even if Cloudinary upload fails
        
        # Generate unique namespace for document ingestion
        namespace_num = uuid.uuid4().hex
        
        ingest_document(pdf_file, pdf_filename, namespace_num)
        
        # Extract hierarchy using RAG
        hierarchy_query = "Give me topics subtopics hairarchy of the document in json format, it should be detailed hairarchy, the naming should match the name present in the docs, points should be detailed, with depth, image prompt accurate. cover complete document"
        extracted_hierarchy = ask_question(
            question=hierarchy_query, 
            namespace=namespace_num, 
            prompt_type=PromptType.HIERARCHY_EXTRACTION
        )
        
        # Create source with Cloudinary PDF link
        source = Source(
            sourceType=SourceType.Document,
            document=namespace_num,
            extractedHierarchy=extracted_hierarchy,
            link=pdf_link,  # Store Cloudinary URL in link field
            classroom_id=obj.id
        )
        session.add(source)
        session.commit()
    
    return obj

def get_classrooms(session: Session):
    return session.exec(select(Classroom)).all()

def get_classroom_by_id(id: UUID, session: Session):
    return session.get(Classroom, id)

def update_classroom(id: UUID, data, session: Session):
    obj = session.get(Classroom, id)
    if not obj:
        return None
    
    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(obj, key, value)
        
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def delete_classroom(id: UUID, session: Session):
    obj = session.get(Classroom, id)
    if not obj:
        return None
    session.delete(obj)
    session.commit()
    return True
