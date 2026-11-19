import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.database.models import User, Client, ApiCredential, TryonHistory, UsageRecord
from src.auth.security import decode_access_token, hash_api_key


def resolve_user_from_headers(headers: Any, db: Session) -> Optional[User]:
    """
    Attempts to identify the authenticated user from incoming HTTP headers.
    Supports either:
      1. 'Authorization: Bearer <JWT>'
      2. 'X-API-Key: <nutz_live_...>'
    Returns User if valid and active, else None.
    """
    # 1. Bearer Token
    auth_header = headers.get("authorization") or headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                user_id = uuid.UUID(payload["sub"])
                user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
                if user:
                    return user
            except Exception:
                pass

    # 2. X-API-Key
    api_key = headers.get("x-api-key") or headers.get("X-API-Key")
    if api_key:
        key_hash = hash_api_key(api_key)
        now = datetime.now(timezone.utc)
        credential = db.query(ApiCredential).filter(
            ApiCredential.key_hash == key_hash,
            ApiCredential.revoked_at.is_(None)
        ).first()

        if credential and (credential.expires_at is None or credential.expires_at > now):
            if (
                credential.client
                and credential.client.account_status in ("approved", "active")
                and credential.client.user
                and credential.client.user.is_active
            ):
                return credential.client.user

    return None


def record_tryon_history_and_usage(
    user_id: uuid.UUID,
    client_id: Optional[uuid.UUID] = None,
    garment_category: Optional[str] = None,
    input_image_reference: Optional[str] = None,
    output_image_reference: Optional[str] = None,
    generation_status: str = "completed",
    operation_type: str = "intelligent_tryon"
) -> Optional[TryonHistory]:
    """
    Safely creates a TryonHistory record and increments a UsageRecord in PostgreSQL.
    """
    db = SessionLocal()
    try:
        history_item = TryonHistory(
            user_id=user_id,
            client_id=client_id,
            garment_category=garment_category,
            input_image_reference=input_image_reference,
            output_image_reference=output_image_reference,
            generation_status=generation_status
        )
        db.add(history_item)

        usage_item = UsageRecord(
            user_id=user_id,
            client_id=client_id,
            operation_type=operation_type,
            usage_count=1
        )
        db.add(usage_item)

        db.commit()
        db.refresh(history_item)
        return history_item
    except Exception as err:
        db.rollback()
        print(f"[Database Error] Could not record tryon history: {err}")
        return None
    finally:
        db.close()
