from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Profile, User
from src.schemas.schemas import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["profiles"])


# PUBLIC_INTERFACE
@router.get("", response_model=list[ProfileOut], summary="List profiles for current user")
def list_profiles(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all profiles belonging to current user."""
    return db.query(Profile).filter(Profile.user_id == current_user.id).all()


# PUBLIC_INTERFACE
@router.post("", response_model=ProfileOut, summary="Create a new profile")
def create_profile(payload: ProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new profile under current user's account."""
    exists = db.query(Profile).filter(Profile.user_id == current_user.id, Profile.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Profile name already exists.")
    profile = Profile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# PUBLIC_INTERFACE
@router.put("/{profile_id}", response_model=ProfileOut, summary="Update profile by id")
def update_profile(
    profile_id: int,
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing profile."""
    profile = db.get(Profile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Profile not found.")
    for k, v in payload.model_dump().items():
        setattr(profile, k, v)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# PUBLIC_INTERFACE
@router.delete("/{profile_id}", summary="Delete profile by id", status_code=204)
def delete_profile(profile_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a profile by id."""
    profile = db.get(Profile, profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Profile not found.")
    db.delete(profile)
    db.commit()
    return None
