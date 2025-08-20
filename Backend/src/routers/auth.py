from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.models import User
from src.schemas.schemas import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


# PUBLIC_INTERFACE
@router.post("/register", response_model=UserOut, summary="Register a new user")
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account with email and password.

    Validates that the email and (if provided) phone are unique to prevent database
    integrity errors and return friendly 400 messages instead of 500s.
    """
    # Email uniqueness check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Optional phone uniqueness check (phone has a unique constraint in the DB)
    if payload.phone:
        phone_owner = db.query(User).filter(User.phone == payload.phone).first()
        if phone_owner:
            raise HTTPException(status_code=400, detail="Phone already registered.")

    user = User(
        email=payload.email,
        phone=payload.phone,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Roll back and return a clear error in case of rare race conditions or other constraint issues
        db.rollback()
        raise HTTPException(status_code=400, detail="User with provided email/phone already exists.")
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.post("/login", response_model=Token, summary="Login and receive JWT")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate with email and password to receive a JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(subject={"user_id": user.id}, expires_delta=timedelta(minutes=60))
    return Token(access_token=access_token, token_type="bearer")
