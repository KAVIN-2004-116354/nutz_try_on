import uuid
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from src.database.connection import get_db
from src.database.models import (
    User,
    Client,
    ApiCredential,
    TryonHistory,
    UsageRecord,
    RevokedToken,
    PasswordResetToken,
    EmailVerificationToken,
)
from src.database.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    TokenResponse,
    ClientCreate,
    ClientResponse,
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    TryonHistoryResponse,
    UsageRecordResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    GenericMessageResponse,
)
from src.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_api_key,
    generate_action_token,
    hash_token,
)
from src.auth.dependencies import (
    bearer_scheme,
    get_current_user,
    get_current_active_user,
    require_verified_user,
    get_authenticated_client,
    require_role,
)
from src.services.email_service import (
    send_verification_email,
    send_password_reset_email,
)

router = APIRouter(prefix="/api/v1", tags=["Authentication & Client Management"])

# In-memory sliding window rate limiter
# { key: [timestamp1, timestamp2, ...] }
_rate_limit_cache: Dict[str, List[float]] = {}


def check_rate_limit(key: str, max_requests: int = 4, window_seconds: int = 600) -> bool:
    """
    Sliding window rate limit checker.
    Returns True if allowed, False if exceeded.
    """
    now = time.time()
    records = _rate_limit_cache.get(key, [])
    records = [t for t in records if now - t < window_seconds]
    if len(records) >= max_requests:
        _rate_limit_cache[key] = records
        return False
    records.append(now)
    _rate_limit_cache[key] = records
    return True


# ============================================================================
# User Registration & Authentication
# ============================================================================

@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user account with Argon2id password hashing.
    Validates input, checks for duplicate email, generates verification token,
    and returns initial access token.
    """
    clean_email = user_in.email.strip().lower()
    clean_name = user_in.full_name.strip()

    if len(clean_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name must be at least 2 characters long"
        )

    # Check for duplicate email
    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{clean_email}' already exists. Please sign in."
        )

    # Hash password with Argon2id
    password_hash = hash_password(user_in.password)
    now_utc = datetime.now(timezone.utc)

    new_user = User(
        full_name=clean_name,
        email=clean_email,
        password_hash=password_hash,
        phone=user_in.phone.strip() if user_in.phone else None,
        role=user_in.role or "user",
        is_active=True,
        email_verified=False,
        created_at=now_utc,
        updated_at=now_utc,
        last_login=now_utc,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If role is client, automatically create linked Client profile
    if new_user.role == "client":
        client_profile = Client(
            user_id=new_user.id,
            company_name=clean_name,
            contact_email=clean_email,
            phone=new_user.phone,
            account_status="active",
        )
        db.add(client_profile)
        db.commit()

    # Create verification token record (24 hour expiry)
    raw_vtoken, vtoken_hash = generate_action_token()
    v_record = EmailVerificationToken(
        user_id=new_user.id,
        token_hash=vtoken_hash,
        expires_at=now_utc + timedelta(hours=24),
        used_at=None,
        created_at=now_utc
    )
    db.add(v_record)
    db.commit()

    # Send verification email safely
    try:
        send_verification_email(new_user.email, raw_vtoken, expires_in_hours=24)
    except Exception:
        pass

    # Issue JWT token (includes jti claim)
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role}
    )

    user_resp = UserResponse.model_validate(new_user)
    return TokenResponse(
        access_token=access_token,
        token=access_token,
        token_type="bearer",
        user=user_resp,
    )


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Authenticate user and obtain JWT token"
)
async def login_user(
    request: Request,
    credentials: Optional[UserLogin] = None,
    db: Session = Depends(get_db)
):
    """
    Authenticates a user using email and password against Argon2id hash.
    Accepts JSON body or Form data.
    Updates last_login timestamp and returns signed JWT access token.
    """
    clean_email = ""
    password = ""

    if credentials and credentials.email:
        clean_email = credentials.email.strip().lower()
        password = credentials.password
    else:
        try:
            body = await request.json()
            raw_email = body.get("email") or body.get("username") or ""
            clean_email = raw_email.strip().lower()
            password = body.get("password") or ""
        except Exception:
            try:
                form = await request.form()
                raw_email = form.get("email") or form.get("username") or ""
                clean_email = str(raw_email).strip().lower()
                password = str(form.get("password") or "")
            except Exception:
                pass

    if not clean_email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    user = db.query(User).filter(User.email == clean_email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    user_resp = UserResponse.model_validate(user)
    return TokenResponse(
        access_token=access_token,
        token=access_token,
        token_type="bearer",
        user=user_resp,
    )


# ============================================================================
# Feature A: Secure Logout
# ============================================================================

@router.post(
    "/auth/logout",
    response_model=GenericMessageResponse,
    summary="Securely log out and revoke current access token session"
)
def logout_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    """
    Securely terminates the active session:
    1. Extracts JWT jti claim from token (handling expired tokens gracefully).
    2. Records the revoked token in RevokedToken.
    3. Guarantees token isolation and idempotency.
    """
    if not auth_credentials or not auth_credentials.credentials:
        return GenericMessageResponse(status="success", message="Logged out successfully")

    token = auth_credentials.credentials
    # Decode without verifying expiration so already-expired tokens can be revoked cleanly
    payload = decode_access_token(token, verify_exp=False)
    if not payload:
        return GenericMessageResponse(status="success", message="Logged out successfully")

    jti = payload.get("jti")
    sub = payload.get("sub")
    exp = payload.get("exp")

    if jti and sub:
        try:
            user_uuid = uuid.UUID(sub)
            now_utc = datetime.now(timezone.utc)
            if exp:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            else:
                expires_at = now_utc + timedelta(hours=24)

            # Prevent duplicate insertion if already revoked
            existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if not existing:
                revocation_record = RevokedToken(
                    jti=jti,
                    user_id=user_uuid,
                    expires_at=expires_at,
                    revoked_at=now_utc,
                    created_at=now_utc
                )
                db.add(revocation_record)
                db.commit()
        except Exception:
            db.rollback()

    return GenericMessageResponse(status="success", message="Logged out successfully")


# ============================================================================
# Feature B: Password Reset
# ============================================================================

@router.post(
    "/auth/forgot-password",
    response_model=GenericMessageResponse,
    summary="Request password reset instructions"
)
def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Initiates password reset:
    - Returns identical generic response whether email exists or not.
    - Rate limits requests to prevent enumeration and denial of service.
    - Generates high-entropy token, stores only SHA-256 hash.
    - Sets 30 minute single-use expiration.
    """
    clean_email = req.email.strip().lower()
    client_ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(f"forgot:{client_ip}:{clean_email}", max_requests=4, window_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please wait a few moments before trying again."
        )

    user = db.query(User).filter(User.email == clean_email).first()
    if user and user.is_active:
        now_utc = datetime.now(timezone.utc)

        # Invalidate older unused reset tokens
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None)
        ).update({"used_at": now_utc})

        raw_token, token_hash = generate_action_token()
        reset_entry = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now_utc + timedelta(minutes=30),
            used_at=None,
            created_at=now_utc
        )
        db.add(reset_entry)
        db.commit()

        try:
            send_password_reset_email(user.email, raw_token, expires_in_minutes=30)
        except Exception:
            pass

    return GenericMessageResponse(
        status="success",
        message="If this email is registered, password reset instructions have been sent."
    )


@router.post(
    "/auth/reset-password",
    response_model=GenericMessageResponse,
    summary="Reset password using reset token"
)
def reset_password(
    req: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Resets password:
    - Validates token hash and expiration.
    - Rejects used, invalid, or expired tokens.
    - Hashes new password with Argon2id.
    - Revokes all existing JWT sessions by updating password_changed_at.
    """
    if len(req.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be at least 8 characters long"
        )

    token_hash = hash_token(req.token)
    now_utc = datetime.now(timezone.utc)

    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    if not reset_record or reset_record.used_at is not None or reset_record.expires_at < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used reset token."
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account associated with this token not found."
        )

    # Update password with Argon2id and invalidate all prior sessions
    user.password_hash = hash_password(req.new_password)
    user.password_changed_at = now_utc
    user.updated_at = now_utc
    reset_record.used_at = now_utc

    db.commit()

    return GenericMessageResponse(
        status="success",
        message="Password has been successfully reset. Please sign in with your new password."
    )


# ============================================================================
# Feature C: Email Verification
# ============================================================================

@router.post(
    "/auth/verify-email",
    response_model=GenericMessageResponse,
    summary="Verify user email address using token"
)
def verify_email(
    req: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verifies user's email address:
    - Validates verification token hash and expiration.
    - Marks email_verified = True.
    - Marks token as used.
    """
    token_hash = hash_token(req.token)
    now_utc = datetime.now(timezone.utc)

    record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token_hash == token_hash
    ).first()

    if not record or record.used_at is not None or record.expires_at < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already used verification token."
        )

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account associated with this token not found."
        )

    user.email_verified = True
    user.updated_at = now_utc
    record.used_at = now_utc

    db.commit()

    return GenericMessageResponse(
        status="success",
        message="Email address has been successfully verified."
    )


@router.post(
    "/auth/resend-verification",
    response_model=GenericMessageResponse,
    summary="Resend email verification link"
)
def resend_verification(
    req: ResendVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resends verification email:
    - Rate limited to prevent spam.
    - Invalidates older unused tokens.
    - Returns generic message to prevent account enumeration.
    """
    clean_email = req.email.strip().lower()
    client_ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(f"resend:{client_ip}:{clean_email}", max_requests=4, window_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification requests. Please wait a few moments before trying again."
        )

    user = db.query(User).filter(User.email == clean_email).first()
    if user and user.is_active and not user.email_verified:
        now_utc = datetime.now(timezone.utc)

        # Invalidate older unused tokens
        db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None)
        ).update({"used_at": now_utc})

        raw_token, token_hash = generate_action_token()
        token_entry = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now_utc + timedelta(hours=24),
            used_at=None,
            created_at=now_utc
        )
        db.add(token_entry)
        db.commit()

        try:
            send_verification_email(user.email, raw_token, expires_in_hours=24)
        except Exception:
            pass

    return GenericMessageResponse(
        status="success",
        message="If this email is associated with an unverified account, a verification link has been sent."
    )


# ============================================================================
# User Profile Management
# ============================================================================

@router.get(
    "/auth/me",
    summary="Get current authenticated user profile"
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Returns the authenticated user's profile with backward-compatible format.
    """
    return {
        "authenticated": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.full_name,
            "full_name": current_user.full_name,
            "phone": current_user.phone,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "password_changed_at": current_user.password_changed_at.isoformat() if current_user.password_changed_at else None,
        }
    }


@router.put(
    "/auth/me",
    response_model=UserResponse,
    summary="Update current user profile"
)
def update_me(
    profile_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if profile_in.full_name is not None:
        clean_name = profile_in.full_name.strip()
        if len(clean_name) >= 2:
            current_user.full_name = clean_name
    if profile_in.phone is not None:
        current_user.phone = profile_in.phone.strip()

    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.get(
    "/auth/verified-only-test",
    summary="Protected endpoint requiring email verification"
)
def verified_only_endpoint(current_user: User = Depends(require_verified_user)):
    """Enforces email_verified requirement for sensitive atelier operations."""
    return {
        "status": "success",
        "message": "Access granted to verified patron",
        "user_id": str(current_user.id)
    }


# ============================================================================
# Client Profile Management
# ============================================================================

@router.post(
    "/clients",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a client organization for current user"
)
def create_client_profile(
    client_in: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    existing_client = db.query(Client).filter(Client.user_id == current_user.id).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A client organization is already associated with this account"
        )

    # Automatically upgrade role to client if user
    if current_user.role == "user":
        current_user.role = "client"

    client = Client(
        user_id=current_user.id,
        company_name=client_in.company_name.strip(),
        website=client_in.website.strip() if client_in.website else None,
        contact_email=client_in.contact_email or current_user.email,
        phone=client_in.phone or current_user.phone,
        business_type=client_in.business_type,
        account_status="active",
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return ClientResponse.model_validate(client)


@router.get(
    "/clients/me",
    response_model=ClientResponse,
    summary="Retrieve current client organization profile"
)
def get_my_client_profile(client: Client = Depends(get_authenticated_client)):
    return ClientResponse.model_validate(client)


# ============================================================================
# API Key Credentials Management
# ============================================================================

@router.post(
    "/api-keys",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a cryptographically secure API key (shown once)"
)
def create_api_key(
    key_in: ApiKeyCreate,
    client: Client = Depends(get_authenticated_client),
    db: Session = Depends(get_db)
):
    """
    Generates a cryptographically secure API key.
    Stores only the SHA-256 hash. Returns the unmasked key once.
    """
    raw_key, prefix, key_hash = generate_api_key()

    expires_at = None
    if key_in.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_in.expires_in_days)

    api_cred = ApiCredential(
        client_id=client.id,
        key_prefix=prefix,
        key_hash=key_hash,
        name=key_in.name or "Default API Key",
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at,
    )
    db.add(api_cred)
    db.commit()
    db.refresh(api_cred)

    return ApiKeyCreatedResponse(
        id=api_cred.id,
        name=api_cred.name,
        key_prefix=api_cred.key_prefix,
        api_key=raw_key,
        created_at=api_cred.created_at,
        expires_at=api_cred.expires_at,
    )


@router.get(
    "/api-keys",
    response_model=List[ApiKeyResponse],
    summary="List all API keys for client"
)
def list_api_keys(
    client: Client = Depends(get_authenticated_client),
    db: Session = Depends(get_db)
):
    keys = db.query(ApiCredential).filter(
        ApiCredential.client_id == client.id
    ).order_by(desc(ApiCredential.created_at)).all()
    return [ApiKeyResponse.model_validate(k) for k in keys]


@router.delete(
    "/api-keys/{key_id}",
    summary="Revoke an API key"
)
def revoke_api_key(
    key_id: uuid.UUID,
    client: Client = Depends(get_authenticated_client),
    db: Session = Depends(get_db)
):
    key = db.query(ApiCredential).filter(
        ApiCredential.id == key_id,
        ApiCredential.client_id == client.id
    ).first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    if key.revoked_at is not None:
        return {"status": "success", "message": "API key is already revoked"}

    key.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "success", "message": "API key has been revoked successfully"}


# ============================================================================
# Tryon History & Usage Endpoints
# ============================================================================

@router.get(
    "/tryon/history",
    response_model=List[TryonHistoryResponse],
    summary="Retrieve user's virtual try-on history"
)
def get_user_tryon_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    Returns virtual try-on history records for the authenticated user,
    ordered with the most recent first.
    """
    history = db.query(TryonHistory).filter(
        TryonHistory.user_id == current_user.id
    ).order_by(desc(TryonHistory.created_at)).offset(offset).limit(limit).all()
    return [TryonHistoryResponse.model_validate(h) for h in history]


@router.get(
    "/usage/summary",
    summary="Retrieve usage statistics for the authenticated user or client"
)
def get_usage_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Returns total operations performed grouped by operation_type.
    """
    records = db.query(
        UsageRecord.operation_type,
        func.sum(UsageRecord.usage_count).label("total_count"),
        func.count(UsageRecord.id).label("total_requests")
    ).filter(
        UsageRecord.user_id == current_user.id
    ).group_by(UsageRecord.operation_type).all()

    summary = {
        row.operation_type: {
            "total_count": int(row.total_count or 0),
            "total_requests": int(row.total_requests or 0)
        }
        for row in records
    }
    return {
        "user_id": str(current_user.id),
        "usage_summary": summary
    }
