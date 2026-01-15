from uuid import UUID
from sqlmodel import Session, select
from app.models.learner import Learner
from app.core.security import get_password_hash

def create_learner(learner_data, session: Session):
    hashed_password = get_password_hash(learner_data.password)
    learner = Learner(
        name=learner_data.name, 
        email=learner_data.email, 
        password=hashed_password
    )
    session.add(learner)
    session.commit()
    session.refresh(learner)
    return learner

def get_learners(session: Session):
    return session.exec(select(Learner)).all()

def get_learner_by_id(learner_id: UUID, session: Session):
    return session.get(Learner, learner_id)

def get_learner_by_email(email: str, session: Session):
    statement = select(Learner).where(Learner.email == email)
    return session.exec(statement).first()

def update_learner(learner_id: UUID, learner_data, session: Session):
    learner = session.get(Learner, learner_id)
    if not learner:
        return None

    if learner_data.name:
        learner.name = learner_data.name
    if learner_data.password:
        learner.password = get_password_hash(learner_data.password)

    session.add(learner)
    session.commit()
    session.refresh(learner)
    return learner

def delete_learner(learner_id: UUID, session: Session):
    learner = session.get(Learner, learner_id)
    if not learner:
        return None

    session.delete(learner)
    session.commit()
    return True
