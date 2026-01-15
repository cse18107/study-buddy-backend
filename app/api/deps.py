from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from app.core.config import settings
from app.core.database import get_session
from app.models.learner import Learner
from app.services.learner_service import get_learner_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_current_learner(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Learner:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    learner = get_learner_by_email(email, session)
    if learner is None:
        raise credentials_exception
    return learner
