import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import User, Client, ApiCredential, RevokedToken
from src.auth.security import decode_access_token, hash_api_key

# Optional Bearer Token Header Scheme
bearer_scheme = HTTPBearer(auto_error=False)

# Optional X-API-Key Header Scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates JWT Bearer token from Authorization header.
    Validates expiration, ensures jti is not in RevokedToken,
    and checks if the session predates a password change.
    Returns the authenticated User or raises 401 Unauthorized.
    """
    if not auth_credentials or not auth_credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Check if token's jti has been explicitly revoked
    jti = payload.get("jti")
    if jti:
        revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user identifier in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with this token does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Please contact support."
        )

    # 2. Check if user changed password after this token was issued
    iat = payload.get("iat")
    if user.password_changed_at and iat:
        iat_dt = datetime.fromtimestamp(iat, tz=timezone.utc)
        if iat_dt < user.password_changed_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired due to a recent password reset. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Validates that current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


def require_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Enforces email verification requirement on protected endpoints."""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address has not been verified. Please verify your email before accessing this feature."
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of roles {allowed_roles}, your role is '{current_user.role}'"
            )
        return current_user
    return role_checker


def get_optional_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Returns authenticated User if either a valid Bearer token or valid X-API-Key is provided.
    Rejects revoked tokens and sessions invalidated by password change.
    If no credentials or invalid/revoked credentials are supplied, returns None without error.
    """
    # 1. Check Bearer Token
    if auth_credentials and auth_credentials.credentials:
        payload = decode_access_token(auth_credentials.credentials)
        if payload and "sub" in payload:
            jti = payload.get("jti")
            if jti:
                revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
                if revoked:
                    return None

            try:
                user_uuid = uuid.UUID(payload["sub"])
                user = db.query(User).filter(User.id == user_uuid, User.is_active.is_(True)).first()
                if user:
                    iat = payload.get("iat")
                    if user.password_changed_at and iat:
                        iat_dt = datetime.fromtimestamp(iat, tz=timezone.utc)
                        if iat_dt < user.password_changed_at:
                            return None
                    return user
            except Exception:
                pass

    # 2. Check X-API-Key
    if api_key:
        key_hash = hash_api_key(api_key)
        now = datetime.now(timezone.utc)
        credential = db.query(ApiCredential).filter(
            ApiCredential.key_hash == key_hash,
            ApiCredential.revoked_at.is_(None)
        ).first()

        if credential:
            if credential.expires_at is None or credential.expires_at > now:
                if credential.client and credential.client.user and credential.client.user.is_active:
                    return credential.client.user

    return None


def get_authenticated_client(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Client:
    """Ensures the authenticated user has an active Client profile."""
    client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No client profile found for current user account. Please create a client profile first."
        )
    if client.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Client account is {client.account_status}. Please contact administrator."
        )
    return client
