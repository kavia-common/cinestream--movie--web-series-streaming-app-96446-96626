from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class ContentCategory(str, Enum):
    TRENDING = "Trending"
    LATEST = "Latest"
    ORIGINALS = "Originals"
    RECOMMENDED = "Recommended"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(32), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    avatar = Column(String(512), nullable=True)
    maturity_rating = Column(String(32), nullable=True, default="PG-13")

    user = relationship("User", back_populates="profiles")
    watchlist_items = relationship("WatchlistItem", back_populates="profile", cascade="all, delete-orphan")
    reviews = relationship("RatingReview", back_populates="profile", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_profile_user_name"),)


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    release_year = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    genre = Column(String(128), nullable=True, index=True)
    language = Column(String(64), nullable=True, index=True)
    category = Column(String(32), nullable=True, index=True)
    is_premium = Column(Boolean, default=False)
    video_url = Column(String(1024), nullable=True)  # For demo, direct URL or path
    thumbnail_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    watchlisted_by = relationship("WatchlistItem", back_populates="content")
    reviews = relationship("RatingReview", back_populates="content")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="watchlist_items")
    content = relationship("Content", back_populates="watchlisted_by")

    __table_args__ = (UniqueConstraint("profile_id", "content_id", name="uq_watchlist_profile_content"),)


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String(8), default="USD", nullable=False)
    quality_limit = Column(String(16), default="1080p", nullable=False)
    screens = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), default="active", nullable=False)  # active, cancelled, expired
    start_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(8), default="USD", nullable=False)
    provider = Column(String(32), nullable=False)  # stripe, paypal, upi
    provider_ref = Column(String(128), nullable=True)  # intent id / transaction id
    status = Column(String(32), default="succeeded", nullable=False)  # succeeded, failed, pending
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="payments")

    __table_args__ = (CheckConstraint("amount_cents >= 0", name="chk_payment_amount_nonnegative"),)


class RatingReview(Base):
    __tablename__ = "rating_reviews"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="reviews")
    content = relationship("Content", back_populates="reviews")

    __table_args__ = (
        UniqueConstraint("profile_id", "content_id", name="uq_review_profile_content"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_rating_range"),
    )
