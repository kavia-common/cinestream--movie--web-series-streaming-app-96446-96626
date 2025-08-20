from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.models import Payment, Subscription, SubscriptionPlan, User
from src.schemas.schemas import PaymentCreate, PaymentOut, PlanCreate, PlanOut, SubscriptionOut
from src.services.payments import PaymentError, get_payment_provider

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# PUBLIC_INTERFACE
@router.get("/plans", response_model=list[PlanOut], summary="List subscription plans")
def list_plans(db: Session = Depends(get_db)):
    """List all active subscription plans."""
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active.is_(True)).all()


# PUBLIC_INTERFACE
@router.post("/plans", response_model=PlanOut, tags=["admin"], summary="Create a new plan (admin)")
def create_plan(payload: PlanCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Admin: Create a subscription plan."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    exists = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Plan name already exists.")
    plan = SubscriptionPlan(**payload.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


# PUBLIC_INTERFACE
@router.post("/subscribe/{plan_id}", response_model=SubscriptionOut, summary="Subscribe to a plan")
def subscribe_to_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Subscribe the current user to a plan."""
    plan = db.get(SubscriptionPlan, plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not found.")
    # deactivate existing
    db.query(Subscription).filter(Subscription.user_id == current_user.id, Subscription.status == "active").update(
        {"status": "cancelled"}
    )
    sub = Subscription(user_id=current_user.id, plan_id=plan.id, status="active", start_at=datetime.utcnow())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


# PUBLIC_INTERFACE
@router.post("/pay", response_model=PaymentOut, summary="Make a subscription payment")
def make_payment(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Perform a payment with the specified provider (simulated)."""
    try:
        provider = get_payment_provider(payload.provider)
    except PaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    status, ref = provider.charge(payload.amount_cents, payload.currency, payload.token)
    payment = Payment(
        user_id=current_user.id,
        amount_cents=payload.amount_cents,
        currency=payload.currency,
        provider=payload.provider,
        provider_ref=ref,
        status=status,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    if status != "succeeded":
        raise HTTPException(status_code=402, detail="Payment failed.")
    return payment


# PUBLIC_INTERFACE
@router.get("/me", response_model=list[SubscriptionOut], summary="List my subscriptions")
def list_my_subscriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List user's subscriptions with plan details."""
    subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    return subs
