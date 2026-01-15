from uuid import UUID
from sqlmodel import Session, select
from app.models.source import Source

def create_source(source_data, session: Session):
    # Map Pydantic model with classroomId to DB model with classroom_id
    data = source_data.model_dump()
    if 'classroomId' in data:
         data['classroom_id'] = data.pop('classroomId')
    source = Source.model_validate(data)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source

def get_sources(session: Session):
    return session.exec(select(Source)).all()

def get_source_by_id(sourceId: UUID, session: Session):
    return session.get(Source, sourceId)

def update_source(sourceId: UUID, source_data, session: Session):
    source = session.get(Source, sourceId)
    if not source:
        return None
    
    source_data_dict = source_data.model_dump(exclude_unset=True)
    if 'classroomId' in source_data_dict:
        source_data_dict['classroom_id'] = source_data_dict.pop('classroomId')

    for key, value in source_data_dict.items():
        setattr(source, key, value)
        
    session.add(source)
    session.commit()
    session.refresh(source)
    return source

def delete_source(sourceId: UUID, session: Session):
    source = session.get(Source, sourceId)
    if not source:
        return None
    session.delete(source)
    session.commit()
    return True

def get_source_by_classroom_and_document(classroomId: UUID, documentId: str, session: Session):
    statement = select(Source).where(Source.classroom_id == classroomId).where(Source.document == documentId)
    return session.exec(statement).first()
