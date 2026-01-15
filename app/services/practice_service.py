from uuid import UUID
from sqlmodel import Session, select
from app.models.practice import Practice

def create_practice(data, session: Session):
    obj = Practice.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_practices(session: Session):
    return session.exec(select(Practice)).all()

def get_practices_by_classroom_id(classroom_id: UUID, session: Session):
    return session.exec(select(Practice).where(Practice.classroom_id == classroom_id)).all()

def get_practice_by_id(id: UUID, session: Session):
    return session.get(Practice, id)

def update_practice(id: UUID, data, session: Session):
    obj = session.get(Practice, id)
    if not obj:
        return None
    
    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(obj, key, value)
        
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def delete_practice(id: UUID, session: Session):
    obj = session.get(Practice, id)
    if not obj:
        return None
    session.delete(obj)
    session.commit()
    return True
