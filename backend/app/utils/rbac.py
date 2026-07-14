"""
Enterprise RBAC (Role-Based Access Control) Utilities
Provides:
- Permission checking
- Site/department filtering
- Session management
- Audit trail logging
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from functools import wraps
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt

from app.config import settings
from app.database import get_db
from app.models.hse_models import (
    SecurityUser, SecurityRole, SecurityPermission,
    SecurityRolePermission, SecurityUserRole, SecuritySession,
    SecurityLoginHistory
)

# Security scheme for OpenAPI
security_scheme = HTTPBearer()

# =============================================
# JWT UTILITIES
# =============================================

def create_access_token(
    user_id: int,
    email: str,
    role_name: str,
    permissions: List[str],
    site_access: List[str],
    session_id: str = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token with RBAC claims.
    """
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role_name,
        "permissions": permissions,
        "site_access": site_access,
        "type": "access",
    }
    if session_id:
        to_encode["session_id"] = session_id

    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int, email: str) -> str:
    """Create JWT refresh token."""
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "type": "refresh",
    }
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    Raises HTTPException if invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =============================================
# AUTHENTICATION
# =============================================

def authenticate_user(db: Session, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Optional[Dict[str, Any]]:
    """
    Authenticate user with email/password.
    Returns user data with tokens if valid, None otherwise.
    Handles account lockout and login history.
    """
    from app.utils.security import verify_password

    # Find user
    user = db.query(SecurityUser).filter(SecurityUser.email == email).first()

    # Log login attempt
    login_history = SecurityLoginHistory(
        user_id=user.user_id if user else None,
        email=email,
        login_type="password",
        ip_address=ip_address,
        user_agent=user_agent,
        login_status="failed",
        failure_reason="User not found"
    )
    db.add(login_history)

    if not user:
        db.commit()
        return None

    # Check if account is locked
    if user.is_locked:
        login_history.login_status = "locked"
        login_history.failure_reason = "Account locked"
        login_history.user_id = user.user_id
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked. Please contact administrator."
        )

    # Check if account is active
    if not user.is_active:
        login_history.login_status = "failed"
        login_history.failure_reason = "Account inactive"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account inactive. Please contact administrator."
        )

    # Verify password
    if not verify_password(password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            login_history.failure_reason = "Account locked after 5 failed attempts"
            login_history.login_status = "locked"
        else:
            login_history.failure_reason = "Invalid password"

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials. {5 - user.failed_login_attempts} attempts remaining."
        )

    # Successful login
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = ip_address
    user.last_login_user_agent = user_agent
    db.commit()

    # Update login history
    login_history.login_status = "success"
    login_history.user_id = user.user_id
    db.commit()

    # Get user roles and permissions
    user_roles = db.query(SecurityUserRole).filter(
        SecurityUserRole.user_id == user.user_id,
        SecurityUserRole.is_active == True
    ).all()

    role_names = []
    site_access = []
    for ur in user_roles:
        role = db.query(SecurityRole).filter(SecurityRole.role_id == ur.role_id).first()
        if role:
            role_names.append(role.role_name)
            if ur.site_access and ur.site_access != "ALL":
                site_access.extend(ur.site_access.split(","))
            elif ur.site_access == "ALL":
                site_access = ["ALL"]
                break

    # Get permissions for all roles
    permissions = []
    for role_name in role_names:
        role = db.query(SecurityRole).filter(SecurityRole.role_name == role_name).first()
        if role:
            role_perms = db.query(SecurityRolePermission).filter(
                SecurityRolePermission.role_id == role.role_id
            ).all()
            for rp in role_perms:
                perm = db.query(SecurityPermission).filter(
                    SecurityPermission.permission_id == rp.permission_id
                ).first()
                if perm:
                    permissions.append(perm.permission_name)

    # Remove duplicates
    permissions = list(set(permissions))
    site_access = list(set(site_access)) if site_access else ["ALL"]

    # Create session first
    import secrets
    session_id = secrets.token_urlsafe(32)
    session = SecuritySession(
        session_id=session_id,
        user_id=user.user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(session)
    db.commit()

    # Create tokens with session_id
    access_token = create_access_token(
        user_id=user.user_id,
        email=user.email,
        role_name=role_names[0] if role_names else "user",
        permissions=permissions,
        site_access=site_access,
        session_id=session_id,
    )
    refresh_token = create_refresh_token(user.user_id, user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role_names[0] if role_names else "user",
        "roles": role_names,
        "permissions": permissions,
        "site_access": site_access,
        "session_id": session_id,
    }


def logout_user(db: Session, user_id: int, session_id: str = None) -> bool:
    """
    Logout user by invalidating session.
    """
    query = db.query(SecuritySession).filter(
        SecuritySession.user_id == user_id,
        SecuritySession.is_active == True
    )

    if session_id:
        query = query.filter(SecuritySession.session_id == session_id)

    sessions = query.all()
    for session in sessions:
        session.is_active = False
        session.logged_out_at = datetime.utcnow()

    db.commit()
    return True


def logout_all_sessions(db: Session, user_id: int) -> int:
    """
    Logout all sessions for a user.
    Returns number of sessions logged out.
    """
    sessions = db.query(SecuritySession).filter(
        SecuritySession.user_id == user_id,
        SecuritySession.is_active == True
    ).all()

    for session in sessions:
        session.is_active = False
        session.logged_out_at = datetime.utcnow()

    db.commit()
    return len(sessions)


# =============================================
# RBAC HELPERS
# =============================================

def get_user_permissions(db: Session, user_id: int) -> List[str]:
    """Get all permissions for a user."""
    user_roles = db.query(SecurityUserRole).filter(
        SecurityUserRole.user_id == user_id,
        SecurityUserRole.is_active == True
    ).all()

    permissions = []
    for ur in user_roles:
        role_perms = db.query(SecurityRolePermission).filter(
            SecurityRolePermission.role_id == ur.role_id
        ).all()
        for rp in role_perms:
            perm = db.query(SecurityPermission).filter(
                SecurityPermission.permission_id == rp.permission_id
            ).first()
            if perm:
                permissions.append(perm.permission_name)

    return list(set(permissions))


def get_user_site_access(db: Session, user_id: int) -> List[str]:
    """Get site access for a user."""
    user_roles = db.query(SecurityUserRole).filter(
        SecurityUserRole.user_id == user_id,
        SecurityUserRole.is_active == True
    ).all()

    site_access = []
    for ur in user_roles:
        if ur.site_access == "ALL":
            return ["ALL"]
        if ur.site_access:
            site_access.extend(ur.site_access.split(","))

    return list(set(site_access)) if site_access else ["ALL"]


def has_permission(user_permissions: List[str], required_permission: str) -> bool:
    """
    Check if user has required permission.
    Supports wildcard: 'dashboard:*' matches 'dashboard:view'
    """
    if not user_permissions:
        return False

    # Direct match
    if required_permission in user_permissions:
        return True

    # Wildcard match: 'dashboard:*' matches 'dashboard:view'
    module = required_permission.split(":")[0] if ":" in required_permission else required_permission
    wildcard = f"{module}:*"
    if wildcard in user_permissions:
        return True

    # Super admin wildcard
    if "admin:*" in user_permissions or "*" in user_permissions or "*:*" in user_permissions:
        return True

    return False


def can_access_site(user_site_access: List[str], requested_site: str) -> bool:
    """Check if user can access requested site."""
    if not user_site_access:
        return False
    if "ALL" in user_site_access:
        return True
    return requested_site in user_site_access


# =============================================
# FASTAPI DEPENDENCIES
# =============================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user from JWT.
    Validates token and returns user info.
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Verify user exists and is active
    user = db.query(SecurityUser).filter(SecurityUser.user_id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    if user.is_locked:
        raise HTTPException(status_code=403, detail="Account locked")

    # Verify session is active
    session = db.query(SecuritySession).filter(
        SecuritySession.session_id == payload.get("session_id"),
        SecuritySession.is_active == True,
        SecuritySession.expires_at > datetime.utcnow()
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    # Update last activity
    session.last_activity_at = datetime.utcnow()
    db.commit()

    return {
        "user_id": user.user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": payload.get("role"),
        "roles": payload.get("roles", [payload.get("role")]),
        "permissions": payload.get("permissions", []),
        "site_access": payload.get("site_access", ["ALL"]),
        "session_id": payload.get("session_id"),
    }


def require_permission(permission: str):
    """
    Decorator to require specific permission.
    Usage: @require_permission("incident:create")
    """
    async def dependency(current_user: Dict = Depends(get_current_user)):
        if not has_permission(current_user["permissions"], permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )
        return current_user
    return dependency


def require_site_access(site_id: str):
    """
    Decorator to require access to specific site.
    Usage: @require_site_access("SITE-A")
    """
    async def dependency(current_user: Dict = Depends(get_current_user)):
        if not can_access_site(current_user["site_access"], site_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to site: {site_id}"
            )
        return current_user
    return dependency


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns None if not authenticated.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# =============================================
# PASSWORD UTILITIES
# =============================================

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password against policy:
    - Minimum 12 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 number
    - At least 1 symbol
    """
    issues = []

    if len(password) < 12:
        issues.append("Password must be at least 12 characters")

    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one symbol")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "strength": "strong" if len(issues) == 0 else "weak"
    }


def is_password_expired(password_changed_at: datetime, expires_at: datetime) -> bool:
    """Check if password has expired."""
    return datetime.utcnow() > expires_at
