from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Content, Payment, Subscription, User

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")


# PUBLIC_INTERFACE
@router.get("/analytics/summary", summary="Basic platform analytics summary")
def analytics_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return basic counts and revenue figures for admin dashboard."""
    ensure_admin(current_user)
    users_count = db.query(func.count(User.id)).scalar() or 0
    content_count = db.query(func.count(Content.id)).scalar() or 0
    active_subs = db.query(func.count(Subscription.id)).filter(Subscription.status == "active").scalar() or 0
    revenue_cents = db.query(func.coalesce(func.sum(Payment.amount_cents), 0)).filter(Payment.status == "succeeded").scalar() or 0
    return {
        "users": users_count,
        "content": content_count,
        "active_subscriptions": active_subs,
        "revenue_cents": int(revenue_cents),
    }
