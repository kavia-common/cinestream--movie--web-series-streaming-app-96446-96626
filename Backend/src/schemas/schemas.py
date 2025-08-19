from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Common / Auth

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    user_id: int = Field(..., description="Authenticated user id")
    exp: Optional[int] = Field(None, description="Expiry timestamp")


class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plain password")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Profiles

class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    avatar: Optional[str] = None
    maturity_rating: Optional[str] = "PG-13"


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


# Content

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    duration_minutes: Optional[int] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    category: Optional[str] = None
    is_premium: bool = False
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(ContentBase):
    pass


class ContentOut(ContentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Watchlist

class WatchlistItemOut(BaseModel):
    id: int
    profile_id: int
    content: 'ContentOut'
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Subscription

class PlanBase(BaseModel):
    name: str
    price_cents: int
    currency: str = "USD"
    quality_limit: str = "1080p"
    screens: int = 1
    is_active: bool = True


class PlanCreate(PlanBase):
    pass


class PlanOut(PlanBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    status: str
    start_at: datetime
    end_at: Optional[datetime] = None
    plan: Optional[PlanOut] = None

    model_config = ConfigDict(from_attributes=True)


# Payments

class PaymentCreate(BaseModel):
    amount_cents: int
    currency: str = "USD"
    provider: str = Field(..., description="stripe|paypal|upi")
    token: str = Field(..., description="payment token or id obtained from provider")


class PaymentOut(BaseModel):
    id: int
    user_id: int
    amount_cents: int
    currency: str
    provider: str
    provider_ref: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Reviews

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class ReviewUpdate(ReviewCreate):
    pass


class ReviewOut(BaseModel):
    id: int
    profile_id: int
    content_id: int
    rating: int
    review_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Streaming

class StreamTokenOut(BaseModel):
    playback_url: str = Field(..., description="URL for HLS/DASH playback with token")
    expires_in: int = Field(..., description="Seconds until expiry")


# Forward references
ContentOut.model_rebuild()
WatchlistItemOut.model_rebuild()
