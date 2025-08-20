from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Content, Profile, RatingReview, User
from src.schemas.schemas import ReviewCreate, ReviewOut, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _ensure_profile(profile_id: int, user: User, db: Session) -> Profile:
    profile = db.get(Profile, profile_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile


# PUBLIC_INTERFACE
@router.get("/content/{content_id}", response_model=list[ReviewOut], summary="List reviews for content")
def list_reviews_for_content(content_id: int, db: Session = Depends(get_db)):
    """List all reviews for a content item."""
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    return db.query(RatingReview).filter(RatingReview.content_id == content_id).all()


# PUBLIC_INTERFACE
@router.post("/{profile_id}/content/{content_id}", response_model=ReviewOut, summary="Add a review")
def add_review(
    profile_id: int,
    content_id: int,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a rating and optional review for content by profile."""
    _ensure_profile(profile_id, current_user, db)
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    existing = (
        db.query(RatingReview)
        .filter(RatingReview.profile_id == profile_id, RatingReview.content_id == content_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Review already exists.")
    review = RatingReview(profile_id=profile_id, content_id=content_id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# PUBLIC_INTERFACE
@router.put("/{review_id}", response_model=ReviewOut, summary="Update a review")
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing review created by one of the user's profiles."""
    review = db.get(RatingReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    profile = db.get(Profile, review.profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed.")
    for k, v in payload.model_dump().items():
        setattr(review, k, v)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# PUBLIC_INTERFACE
@router.delete("/{review_id}", status_code=204, summary="Delete a review")
def delete_review(review_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete an existing review by the owning profile."""
    review = db.get(RatingReview, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    profile = db.get(Profile, review.profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed.")
    db.delete(review)
    db.commit()
    return None
