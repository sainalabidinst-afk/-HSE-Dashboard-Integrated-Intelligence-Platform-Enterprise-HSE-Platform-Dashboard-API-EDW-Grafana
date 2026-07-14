"""
Security utilities for JWT and password handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def validate_password_policy(password: str) -> tuple[bool, str]:
    """
    Validate password against configured policy.
    Returns (is_valid, error_message).
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
    if settings.PASSWORD_REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if settings.PASSWORD_REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if settings.PASSWORD_REQUIRE_NUMBER and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if settings.PASSWORD_REQUIRE_SYMBOL and not any(not c.isalnum() for c in password):
        return False, "Password must contain at least one symbol"
    return True, "Password is valid"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    Payload includes: sub (email), role, site_access, exp, iat, type
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    Raises JWTError if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user from JWT token.
    Use in route: current_user: dict = Depends(get_current_user)
    """
    from fastapi import HTTPException, status
    payload = decode_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {
        "email": email,
        "role": payload.get("role"),
        "site_access": payload.get("site_access", []),
    }


# =============================================
# RBAC DECORATOR
# =============================================

def require_permission(permission: str):
    """
    Decorator to check user permission.
    Usage: @require_permission("can_edit")
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")

            # Check permission (simplified - in production, check against DB)
            permissions = {
                "can_export": current_user.get("can_export", False),
                "can_edit": current_user.get("can_edit", False),
                "can_configure_alerts": current_user.get("can_configure_alerts", False),
            }

            if not permissions.get(permission, False):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission} required"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
