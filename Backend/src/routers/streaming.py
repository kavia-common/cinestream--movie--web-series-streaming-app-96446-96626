
from urllib.parse import urlencode, urlparse, urlunparse

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Content, User
from src.schemas.schemas import StreamTokenOut

router = APIRouter(prefix="/stream", tags=["streaming"])
settings = get_settings()


def _append_query(url: str, params: dict) -> str:
    parts = list(urlparse(url))
    query = dict([kv.split("=") for kv in parts[4].split("&") if kv]) if parts[4] else {}
    query.update(params)
    parts[4] = urlencode(query)
    return urlunparse(parts)


# PUBLIC_INTERFACE
@router.get("/{content_id}", response_model=StreamTokenOut, summary="Get secure playback URL for content")
def get_stream_url(content_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate a signed playback URL for a piece of content."""
    content = db.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    if content.is_premium:
        subs = [s for s in current_user.subscriptions if s.status == "active"]
        if not subs:
            raise HTTPException(status_code=402, detail="Subscription required to stream premium content.")
    token = jwt.encode({"user_id": current_user.id, "content_id": content_id}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    base_url = content.video_url or f"https://cdn.example.com/hls/{content_id}/master.m3u8"
    playback_url = _append_query(base_url, {"token": token})
    return StreamTokenOut(playback_url=playback_url, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
