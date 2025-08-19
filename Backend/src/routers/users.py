from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import User
from src.schemas.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


# PUBLIC_INTERFACE
@router.get("/me", response_model=UserOut, summary="Get current user profile")
def read_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return details about the current authenticated user."""
    return current_user
