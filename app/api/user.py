from fastapi import APIRouter, Depends
from app.api.deps import get_current_learner
from app.models.learner import Learner
from app.schemas.learner import LearnerRead

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=LearnerRead)
def get_me(current_learner: Learner = Depends(get_current_learner)):
    """
    Returns the details of the currently authenticated user.
    """
    return current_learner
