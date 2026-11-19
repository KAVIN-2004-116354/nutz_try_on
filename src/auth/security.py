import os
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import jwt
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# Ensure environment variables are loaded
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "nutz_super_secret_jwt_key_flux_atelier_2026_production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Production-grade Argon2id Password Hasher
# Memory: 64MB (65536KB), Iterations: 3, Parallelism: 4 threads
hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    type=Type.ID
)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using Argon2id."""
    return hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against an Argon2id hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def generate_api_key() -> Tuple[str, str, str]:
    """
    Generates a cryptographically secure random API key.
    Returns:
        raw_key: The full key to display to the user once (e.g. nutz_live_...)
        key_prefix: Short prefix for identification (e.g. nutz_live_a1b2)
        key_hash: SHA-256 hash to store securely in the database
    """
    random_bytes = secrets.token_urlsafe(32)
    raw_key = f"nutz_live_{random_bytes}"
    key_prefix = raw_key[:14]
    key_hash = hash_api_key(raw_key)
    return raw_key, key_prefix, key_hash


def hash_api_key(raw_key: str) -> str:
    """Computes SHA-256 hash of an API key for comparison and storage."""
    return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()


def generate_action_token() -> Tuple[str, str]:
    """
    Generates a cryptographically secure random token for password resets and email verifications.
    Returns:
        raw_token: Sent in link to user's email (never logged or stored in database)
        token_hash: SHA-256 digest stored in database
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash


def hash_token(raw_token: str) -> str:
    """Computes SHA-256 hex digest of a raw token."""
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT access token.
    Guarantees 'jti' (JWT ID) and 'iat' (issued at) claims are present.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if "jti" not in to_encode or not to_encode["jti"]:
        to_encode["jti"] = str(uuid.uuid4())

    to_encode.update({
        "exp": expire,
        "iat": now_utc
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str, verify_exp: bool = True) -> Optional[Dict[str, Any]]:
    """
    Decodes and validates a signed JWT access token.
    If verify_exp is False, allows extracting claims from expired tokens (e.g. for logout).
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
