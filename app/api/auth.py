from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import (
    login_for_access_token, signup_new_user, 
    create_password_reset_token, reset_password
)
from app.schemas.learner import LearnerCreate
from app.schemas.token import Token
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter(tags=["Authentication"])

@router.post("/signup", response_model=Token)
def signup(user_data: LearnerCreate, session: Session = Depends(get_session)):
    try:
        return signup_new_user(session, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    token = login_for_access_token(session, data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# Standard OAuth2 form login (for Swagger UI support)
@router.post("/token", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Convert form data to LoginRequest
    login_request = LoginRequest(email=form_data.username, password=form_data.password)
    token = login_for_access_token(session, login_request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    # In a real application, this would trigger an email.
    # Here we return the token for testing purposes.
    token = create_password_reset_token(data.email)
    return {"message": "Password reset token generated", "reset_token": token}

@router.post("/reset-password")
def reset_password_endpoint(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    success = reset_password(session, data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or user not found"
        )
    return {"message": "Password updated successfully"}
