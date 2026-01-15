from uuid import UUID
from typing import List
from sqlmodel import Session, select
from app.models.question import Question

def create_question(data, session: Session):
    obj = Question.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def get_questions(session: Session):
    return session.exec(select(Question)).all()

def get_question_by_id(id: UUID, session: Session):
    return session.get(Question, id)

def update_question(id: UUID, data, session: Session):
    obj = session.get(Question, id)
    if not obj:
        return None
    
    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(obj, key, value)
        
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj

def delete_question(id: UUID, session: Session):
    obj = session.get(Question, id)
    if not obj:
        return None
    session.delete(obj)
    session.commit()
    return True

def bulk_update_learners_answers(data: List[dict], session: Session):
    updated_ids = []
    for entry in data:
        for q_id, answer in entry.items():
            # Convert string ID to UUID object to avoid StatementError
            try:
                if isinstance(q_id, str):
                    q_id_obj = UUID(q_id)
                else:
                    q_id_obj = q_id
            except ValueError:
                continue

            question = session.get(Question, q_id_obj)
            if question:
                question.learnersAnswer = answer
                session.add(question)
                updated_ids.append(q_id_obj)
    session.commit()
    return updated_ids
