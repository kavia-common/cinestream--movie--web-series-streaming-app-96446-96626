from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Content, User
from src.schemas.schemas import ContentCreate, ContentOut, ContentUpdate

router = APIRouter(prefix="/content", tags=["content"])


# PUBLIC_INTERFACE
@router.get("", response_model=list[ContentOut], summary="List and search content")
def list_content(
    q: Optional[str] = Query(None, description="Search text in title/description"),
    genre: Optional[str] = None,
    language: Optional[str] = None,
    release_year: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List content with optional filtering parameters."""
    query = db.query(Content)
    if q:
        query = query.filter(Content.title.ilike(f"%{q}%"))
    if genre:
        query = query.filter(Content.genre == genre)
    if language:
        query = query.filter(Content.language == language)
    if release_year:
        query = query.filter(Content.release_year == release_year)
    if category:
        query = query.filter(Content.category == category)
    return query.order_by(Content.created_at.desc()).all()


# PUBLIC_INTERFACE
@router.get("/{content_id}", response_model=ContentOut, summary="Get content by id")
def get_content(content_id: int, db: Session = Depends(get_db)):
    """Retrieve content details by id."""
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    return content


# Admin endpoints - require admin

def ensure_admin(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")


# PUBLIC_INTERFACE
@router.post("", response_model=ContentOut, tags=["admin"], summary="Create content (admin)")
def admin_create_content(
    payload: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin: Create new content."""
    ensure_admin(current_user)
    content = Content(**payload.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


# PUBLIC_INTERFACE
@router.put("/{content_id}", response_model=ContentOut, tags=["admin"], summary="Update content (admin)")
def admin_update_content(
    content_id: int,
    payload: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin: Update existing content."""
    ensure_admin(current_user)
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    for k, v in payload.model_dump().items():
        setattr(content, k, v)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


# PUBLIC_INTERFACE
@router.delete("/{content_id}", tags=["admin"], summary="Delete content (admin)", status_code=204)
def admin_delete_content(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Admin: Delete content by id."""
    ensure_admin(current_user)
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    db.delete(content)
    db.commit()
    return None
