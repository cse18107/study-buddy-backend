from datetime import timedelta
from typing import Optional
from sqlmodel import Session
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.services.learner_service import get_learner_by_email, create_learner, update_learner
# schemas
from app.schemas.learner import LearnerCreate
from app.schemas.token import Token
from app.schemas.auth import LoginRequest, ResetPasswordRequest

def authenticate_user(session: Session, email: str, password: str):
    user = get_learner_by_email(email, session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def login_for_access_token(session: Session, form_data: LoginRequest) -> Optional[Token]:
    user = authenticate_user(session, form_data.email, form_data.password)
    if not user:
        return None
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def signup_new_user(session: Session, user_data: LearnerCreate) -> Token:
    user = get_learner_by_email(user_data.email, session)
    if user:
        raise ValueError("Email already registered")
    
    # Create user happens with hashing inside create_learner now
    new_user = create_learner(user_data, session)
    
    # Auto login after signup
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def create_password_reset_token(email: str):
    # In a real app, generate a unique token, save it to DB with expiration, and send email.
    # For now, we will generate a JWT that serves as the reset token.
    expire = timedelta(hours=1)
    reset_token = create_access_token(data={"sub": email, "type": "reset"}, expires_delta=expire)
    return reset_token

def reset_password(session: Session, data: ResetPasswordRequest):
    # Verify token
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(data.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "reset":
            return False
    except JWTError:
        return False
    
    user = get_learner_by_email(email, session)
    if not user:
        return False
    
    user.password = get_password_hash(data.new_password)
    session.add(user)
    session.commit()
    return True
