from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Content, Profile, User, WatchlistItem
from src.schemas.schemas import WatchlistItemOut

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _ensure_profile(profile_id: int, user: User, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile


# PUBLIC_INTERFACE
@router.get("/{profile_id}", response_model=list[WatchlistItemOut], summary="List watchlist for profile")
def list_watchlist(profile_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all content in a profile's watchlist."""
    _ensure_profile(profile_id, current_user, db)
    items = (
        db.query(WatchlistItem)
        .join(Content)
        .filter(WatchlistItem.profile_id == profile_id)
        .order_by(WatchlistItem.created_at.desc())
        .all()
    )
    return items


# PUBLIC_INTERFACE
@router.post("/{profile_id}/add/{content_id}", response_model=WatchlistItemOut, summary="Add content to watchlist")
def add_to_watchlist(
    profile_id: int,
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an item to the profile's watchlist."""
    _ensure_profile(profile_id, current_user, db)
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    existing = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.profile_id == profile_id, WatchlistItem.content_id == content_id)
        .first()
    )
    if existing:
        return existing
    item = WatchlistItem(profile_id=profile_id, content_id=content_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# PUBLIC_INTERFACE
@router.delete("/{profile_id}/remove/{content_id}", status_code=204, summary="Remove content from watchlist")
def remove_from_watchlist(
    profile_id: int,
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an item from the profile's watchlist."""
    _ensure_profile(profile_id, current_user, db)
    item = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.profile_id == profile_id, WatchlistItem.content_id == content_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")
    db.delete(item)
    db.commit()
    return None
