from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.learner import LearnerCreate, LearnerRead, LearnerUpdate
from app.services.learner_service import (
    create_learner, get_learners, get_learner_by_id,
    update_learner, delete_learner
)

router = APIRouter(tags=["Learners"])

@router.post("/", response_model=LearnerRead)
def create(learner: LearnerCreate, session: Session = Depends(get_session)):
    return create_learner(learner, session)

@router.get("/", response_model=list[LearnerRead])
def list_learners(session: Session = Depends(get_session)):
    return get_learners(session)

@router.get("/{learner_id}", response_model=LearnerRead)
def get(learner_id: UUID, session: Session = Depends(get_session)):
    learner = get_learner_by_id(learner_id, session)
    if not learner:
        raise HTTPException(404, "Learner not found")
    return learner

@router.put("/{learner_id}", response_model=LearnerRead)
def update(learner_id: UUID, data: LearnerUpdate, session: Session = Depends(get_session)):
    learner = update_learner(learner_id, data, session)
    if not learner:
        raise HTTPException(404, "Learner not found")
    return learner

@router.delete("/{learner_id}")
def delete(learner_id: UUID, session: Session = Depends(get_session)):
    success = delete_learner(learner_id, session)
    if not success:
        raise HTTPException(404, "Learner not found")
    return {"status": "deleted"}
