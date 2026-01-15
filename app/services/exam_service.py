from uuid import UUID
from sqlmodel import Session, select
from app.models.exam import Exam

def create_exam(data, session: Session):
    obj = Exam.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_exams(session: Session):
    return session.exec(select(Exam)).all()

def get_exam_by_id(id: UUID, session: Session):
    return session.get(Exam, id)

def update_exam(id: UUID, data, session: Session):
    obj = session.get(Exam, id)
    if not obj:
        return None
    
    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(obj, key, value)
        
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def delete_exam(id: UUID, session: Session):
    obj = session.get(Exam, id)
    if not obj:
        return None
    session.delete(obj)
    session.commit()
    return True

def get_exams_by_classroom_id(classroom_id: UUID, session: Session):
    return session.exec(select(Exam).where(Exam.classroom_id == classroom_id)).all()
