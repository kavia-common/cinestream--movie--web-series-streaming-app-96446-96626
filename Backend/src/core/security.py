from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.models.models import User

# Password hashing context (bcrypt)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme: token endpoint matches /auth/login in routers
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_settings = get_settings()


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# PUBLIC_INTERFACE
def create_access_token(
    subject: Union[str, int, Dict[str, Any]],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    The 'subject' can be:
      - a dict (e.g. {"user_id": 123}) which will be merged into claims
      - a string/int which will be stored under the standard 'sub' claim

    Expiration is set via expires_delta or defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    to_encode: Dict[str, Any] = {}

    # Merge provided subject into claims
    if isinstance(subject, dict):
        to_encode.update(subject)
    else:
        to_encode["sub"] = str(subject)

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire

    token = jwt.encode(to_encode, _settings.JWT_SECRET, algorithm=_settings.JWT_ALGORITHM)
    return token


def _decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token. Raises HTTP 401 on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _settings.JWT_SECRET, algorithms=[_settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(_oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency that extracts the current authenticated user from the JWT Bearer token.

    Expects the token to contain either:
      - a 'user_id' claim (preferred, as set by our login), or
      - a string 'sub' claim containing the user id
    """
    payload = _decode_token(token)
    user_id = None

    # Preferred claim set by create_access_token(subject={"user_id": ...})
    if "user_id" in payload:
        user_id = payload.get("user_id")
    # Fallback to standard subject claim
    elif "sub" in payload:
        try:
            user_id = int(payload.get("sub"))
        except (TypeError, ValueError):
            user_id = None

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found.")

    return user
