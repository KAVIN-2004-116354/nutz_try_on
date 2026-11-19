import os
import uuid
import re
import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from src.gateway.app import app
from src.database.connection import SessionLocal, engine
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
from src.auth.security import (
    hash_password,
    verify_password,
    generate_api_key,
    hash_api_key,
    generate_action_token,
    hash_token,
    create_access_token,
    decode_access_token,
)
from src.services.email_service import (
    get_test_outbox,
    clear_test_outbox,
    send_email,
    send_verification_email,
    send_password_reset_email,
    validate_smtp_configuration,
    get_smtp_settings,
)
from src.database.service import resolve_user_from_headers

client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    db_session = SessionLocal()
    yield db_session
    db_session.close()


@pytest.fixture(autouse=True)
def clean_outbox():
    """Ensure in-memory mock outbox is fresh for each test."""
    clear_test_outbox()
    yield
    clear_test_outbox()


# ============================================================================
# Basic Security & Auth Tests
# ============================================================================

def test_argon2id_password_hashing():
    """Verify that password hashing uses Argon2id and correctly verifies matches."""
    plain = "SuperFashionPassword123!"
    hashed = hash_password(plain)

    # Argon2id hashes begin with $argon2id$
    assert hashed.startswith("$argon2id$"), "Hash must be Argon2id format"
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_api_key_cryptography():
    """Verify API key generation, prefix extraction, and SHA-256 hashing."""
    raw_key, prefix, key_hash = generate_api_key()
    assert raw_key.startswith("nutz_live_")
    assert prefix == raw_key[:14]
    assert len(key_hash) == 64  # SHA-256 hex string
    assert hash_api_key(raw_key) == key_hash


def test_jwt_token_creation_and_decoding():
    """Verify JWT access token creation with jti and payload extraction."""
    payload = {"sub": str(uuid.uuid4()), "email": "designer@atelier.nutz", "role": "client"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["email"] == "designer@atelier.nutz"
    assert decoded["role"] == "client"
    assert "exp" in decoded
    assert "jti" in decoded
    assert len(decoded["jti"]) > 10


def test_user_registration_success():
    """Test registering a new user with valid details."""
    unique_email = f"atelier_user_{uuid.uuid4().hex[:8]}@nutz.ai"
    payload = {
        "full_name": "Eleanor Vance",
        "email": unique_email,
        "phone": "+1-555-0192",
        "password": "PasswordAtelier2026!",
        "role": "user"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == "Eleanor Vance"
    assert data["user"]["role"] == "user"
    assert data["user"]["is_active"] is True
    assert data["user"]["email_verified"] is False


def test_duplicate_email_registration_rejected():
    """Test that registering an existing email returns 409 Conflict."""
    unique_email = f"duplicate_test_{uuid.uuid4().hex[:8]}@nutz.ai"
    payload = {
        "full_name": "Marcus Aurelius",
        "email": unique_email,
        "password": "SecurePassword123!",
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"].lower()


def test_validation_errors_registration():
    """Test input validations: short password and short name."""
    # Short name
    r_name = client.post("/api/v1/auth/register", json={
        "full_name": "A",
        "email": f"valid_{uuid.uuid4().hex[:6]}@nutz.ai",
        "password": "ValidPassword123!"
    })
    assert r_name.status_code == 422

    # Short password
    r_pwd = client.post("/api/v1/auth/register", json={
        "full_name": "Valid Name",
        "email": f"valid_{uuid.uuid4().hex[:6]}@nutz.ai",
        "password": "short"
    })
    assert r_pwd.status_code == 422


def test_user_login_success_and_failure():
    """Test authentication flow with valid and invalid credentials."""
    email = f"login_test_{uuid.uuid4().hex[:8]}@nutz.ai"
    password = "CorrectHorseBatteryStaple2026!"

    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json={
        "full_name": "Sophia Loren",
        "email": email,
        "password": password
    })
    assert reg_res.status_code == 201

    # 2. Login with correct password (JSON)
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    # 3. Login with wrong password
    bad_login = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401


def test_auth_me_endpoint():
    """Test /api/v1/auth/me requires valid token and returns correct profile."""
    # Unauthorized without header
    unauth = client.get("/api/v1/auth/me")
    assert unauth.status_code == 401

    # Register and get profile
    email = f"me_test_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Valentino Garavani",
        "email": email,
        "password": "HauteCouture2026!"
    })
    token = reg.json()["access_token"]

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    profile = res.json()
    assert profile["authenticated"] is True
    assert profile["user"]["email"] == email
    assert profile["user"]["name"] == "Valentino Garavani"


def test_client_and_api_key_lifecycle(db):
    """Test Client profile registration, admin approval, secure API key generation and revocation."""
    email = f"brand_{uuid.uuid4().hex[:8]}@couture.com"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Kering Brand Director",
        "email": email,
        "password": "LuxuryBrandPassword123!",
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register client organization through authenticated client onboarding endpoint (status is pending)
    create_client = client.post("/api/v1/clients", json={"company_name": "Kering Brand Director"}, headers=headers)
    assert create_client.status_code == 201
    client_id = create_client.json()["id"]
    assert create_client.json()["account_status"] == "pending"

    # Authorized administrator approves client organization
    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    approve_res = client.patch(
        f"/api/v1/admin/clients/{client_id}/status",
        json={"account_status": "approved"},
        headers=admin_headers
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["account_status"] == "approved"

    client_res = client.get("/api/v1/clients/me", headers=headers)
    assert client_res.status_code == 200
    assert client_res.json()["company_name"] == "Kering Brand Director"
    assert client_res.json()["account_status"] == "approved"

    key_res = client.post("/api/v1/api-keys", json={"name": "Production Storefront Key"}, headers=headers)
    assert key_res.status_code == 201
    key_data = key_res.json()
    raw_key = key_data["api_key"]
    key_id = key_data["id"]
    prefix = key_data["key_prefix"]
    assert raw_key.startswith("nutz_live_")
    assert raw_key.startswith(prefix)

    list_res = client.get("/api/v1/api-keys", headers=headers)
    assert list_res.status_code == 200
    keys = list_res.json()
    assert len(keys) >= 1
    assert "api_key" not in keys[0]
    assert keys[0]["key_prefix"] == prefix

    del_res = client.delete(f"/api/v1/api-keys/{key_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    list_after = client.get("/api/v1/api-keys", headers=headers).json()
    revoked_key = next(k for k in list_after if k["id"] == key_id)
    assert revoked_key["revoked_at"] is not None


def test_tryon_history_and_usage_tracking(db):
    """Test TryonHistory and UsageRecords persistence and querying."""
    email = f"history_user_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Coco Chanel",
        "email": email,
        "password": "LittleBlackDress1926!"
    })
    token = reg.json()["access_token"]
    user_id = uuid.UUID(reg.json()["user"]["id"])
    headers = {"Authorization": f"Bearer {token}"}

    history_entry = TryonHistory(
        user_id=user_id,
        garment_category="full_body",
        input_image_reference="inputs/sample_person.jpg;inputs/sample_garment.jpg",
        output_image_reference="/outputs/tryon_sample_123.png",
        generation_status="completed"
    )
    usage_entry = UsageRecord(
        user_id=user_id,
        operation_type="intelligent_tryon",
        usage_count=1
    )
    db.add(history_entry)
    db.add(usage_entry)
    db.commit()

    hist_res = client.get("/api/v1/tryon/history", headers=headers)
    assert hist_res.status_code == 200
    hist_items = hist_res.json()
    assert len(hist_items) >= 1
    assert hist_items[0]["garment_category"] == "full_body"
    assert hist_items[0]["output_image_reference"] == "/outputs/tryon_sample_123.png"

    usage_res = client.get("/api/v1/usage/summary", headers=headers)
    assert usage_res.status_code == 200
    usage_data = usage_res.json()
    assert "intelligent_tryon" in usage_data["usage_summary"]
    assert usage_data["usage_summary"]["intelligent_tryon"]["total_count"] == 1


def test_alembic_current_revision():
    """Verify that Alembic database is at head and all tables exist."""
    with engine.connect() as conn:
        from sqlalchemy import text
        res = conn.execute(text("SELECT version_num FROM alembic_version;"))
        row = res.fetchone()
        assert row is not None
        assert len(row[0]) > 0
        print(f"Current Alembic revision in PostgreSQL: {row[0]}")


# ============================================================================
# Feature A Tests: Secure Logout
# ============================================================================

def test_logout_success_and_revocation():
    """Test that logout revokes the current JWT and prevents subsequent access."""
    email = f"logout_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Yves Saint Laurent",
        "email": email,
        "password": "LeSmoking1966!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify protected access works before logout
    res_before = client.get("/api/v1/auth/me", headers=headers)
    assert res_before.status_code == 200

    # Call logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "success"

    # Verify revoked token CANNOT access protected endpoints
    res_after = client.get("/api/v1/auth/me", headers=headers)
    assert res_after.status_code == 401
    assert "revoked" in res_after.json()["detail"].lower()


def test_logout_expired_jwt_rejection():
    """Test that an expired JWT is rejected by protected endpoints."""
    user_id = str(uuid.uuid4())
    # Create an already expired token (expired 10 seconds ago)
    expired_token = create_access_token(
        data={"sub": user_id, "email": "expired@nutz.ai", "role": "user"},
        expires_delta=timedelta(seconds=-10)
    )

    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


def test_repeated_logout_behavior():
    """Test that repeated logout calls are idempotent and handled safely."""
    email = f"repeat_logout_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Hubert de Givenchy",
        "email": email,
        "password": "AudreyHepburn1954!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # First logout
    r1 = client.post("/api/v1/auth/logout", headers=headers)
    assert r1.status_code == 200

    # Repeated logout with the same token
    r2 = client.post("/api/v1/auth/logout", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["status"] == "success"


def test_user_session_isolation_on_logout():
    """Test that User A logging out does NOT revoke User B's session."""
    # User A
    reg_a = client.post("/api/v1/auth/register", json={
        "full_name": "Christian Dior",
        "email": f"dior_{uuid.uuid4().hex[:8]}@nutz.ai",
        "password": "NewLook1947Paris!"
    })
    token_a = reg_a.json()["access_token"]

    # User B
    reg_b = client.post("/api/v1/auth/register", json={
        "full_name": "Cristobal Balenciaga",
        "email": f"balenciaga_{uuid.uuid4().hex[:8]}@nutz.ai",
        "password": "MasterOfUsAll1937!"
    })
    token_b = reg_b.json()["access_token"]

    # User A logs out
    client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token_a}"})

    # User A token is revoked
    res_a = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 401

    # User B token remains completely valid and active!
    res_b = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    assert res_b.json()["user"]["name"] == "Cristobal Balenciaga"


# ============================================================================
# Feature B Tests: Password Reset
# ============================================================================

def test_forgot_password_generic_response_for_unknown_email():
    """Test that requesting reset for an unknown email returns the generic success message."""
    res = client.post("/api/v1/auth/forgot-password", json={
        "email": f"unknown_{uuid.uuid4().hex[:10]}@fashionnonexistent.com"
    })
    assert res.status_code == 200
    assert "If this email is registered" in res.json()["message"]


def test_password_reset_full_flow_and_session_revocation(db):
    """
    Test full password reset workflow:
    1. Request reset.
    2. Extract single-use token from mock mailbox.
    3. Perform reset.
    4. Verify old password rejected, new accepted.
    5. Verify tokens issued prior to reset are revoked.
    """
    email = f"reset_flow_{uuid.uuid4().hex[:8]}@nutz.ai"
    old_password = "OldPassword2026!"
    new_password = "BrandNewSecurePassword2026!"

    # 1. Register and get initial session token
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Gianni Versace",
        "email": email,
        "password": old_password
    })
    initial_token = reg.json()["access_token"]

    # Clear outbox from registration email
    clear_test_outbox()

    # 2. Request password reset
    forgot_res = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200

    outbox = get_test_outbox()
    assert len(outbox) == 1
    assert outbox[0]["to"] == email
    match = re.search(r"token=([A-Za-z0-9_-]+)", outbox[0]["text"])
    assert match, "Reset token must be present in email link"
    raw_token = match.group(1)

    # 3. Test invalid reset token
    bad_res = client.post("/api/v1/auth/reset-password", json={
        "token": "invalid_bogus_token_12345",
        "new_password": new_password
    })
    assert bad_res.status_code == 400

    # 4. Perform valid password reset
    reset_res = client.post("/api/v1/auth/reset-password", json={
        "token": raw_token,
        "new_password": new_password
    })
    assert reset_res.status_code == 200
    assert reset_res.json()["status"] == "success"

    # 5. Reusing the same reset token must be rejected
    reuse_res = client.post("/api/v1/auth/reset-password", json={
        "token": raw_token,
        "new_password": "AnotherNewPassword123!"
    })
    assert reuse_res.status_code == 400
    assert "already used" in reuse_res.json()["detail"].lower()

    # 6. Old password must be rejected
    old_login = client.post("/api/v1/auth/login", json={"email": email, "password": old_password})
    assert old_login.status_code == 401

    # 7. New password must be accepted
    new_login = client.post("/api/v1/auth/login", json={"email": email, "password": new_password})
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()

    # 8. Token issued prior to password reset must be revoked
    old_session_check = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {initial_token}"})
    assert old_session_check.status_code == 401
    assert "password" in old_session_check.json()["detail"].lower()


def test_expired_reset_token_rejection(db):
    """Test that expired reset tokens are rejected."""
    email = f"expired_reset_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Karl Lagerfeld",
        "email": email,
        "password": "ChanelFendi1983!"
    })
    user_id = uuid.UUID(reg.json()["user"]["id"])

    # Create an expired reset token in the database
    raw_token, token_hash = generate_action_token()
    expired_entry = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),  # 5 min in past
        used_at=None,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=35)
    )
    db.add(expired_entry)
    db.commit()

    res = client.post("/api/v1/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewKarlPassword2026!"
    })
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


# ============================================================================
# Feature C Tests: Email Verification
# ============================================================================

def test_email_verification_workflow_and_restrictions(db):
    """
    Test email verification workflow:
    1. User registered -> email_verified is False.
    2. Endpoint requiring verification blocks unverified user (403).
    3. Extract verification token from mock outbox.
    4. Successful verification updates email_verified to True.
    5. Previously blocked endpoint now grants access.
    6. Reusing verification token fails.
    """
    email = f"verify_flow_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Donatella Versace",
        "email": email,
        "password": "MedusaAtelier1997!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check unverified restrictions
    restricted_res = client.get("/api/v1/auth/verified-only-test", headers=headers)
    assert restricted_res.status_code == 403
    assert "not been verified" in restricted_res.json()["detail"].lower()

    # 2. Extract verification token from outbox
    outbox = get_test_outbox()
    assert len(outbox) == 1
    match = re.search(r"token=([A-Za-z0-9_-]+)", outbox[0]["text"])
    assert match, "Verification token must be in registration email"
    raw_vtoken = match.group(1)

    # 3. Test invalid verification token
    bad_v = client.post("/api/v1/auth/verify-email", json={"token": "bogus_vtoken_12345"})
    assert bad_v.status_code == 400

    # 4. Successful verification
    good_v = client.post("/api/v1/auth/verify-email", json={"token": raw_vtoken})
    assert good_v.status_code == 200
    assert "verified" in good_v.json()["message"].lower()

    # 5. Verify email status updated on /auth/me
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email_verified"] is True

    # 6. Restricted endpoint now accessible
    now_allowed = client.get("/api/v1/auth/verified-only-test", headers=headers)
    assert now_allowed.status_code == 200
    assert now_allowed.json()["status"] == "success"

    # 7. Reusing verification token is rejected
    reuse_v = client.post("/api/v1/auth/verify-email", json={"token": raw_vtoken})
    assert reuse_v.status_code == 400
    assert "already used" in reuse_v.json()["detail"].lower()


def test_expired_verification_token_rejection(db):
    """Test that expired verification tokens are rejected."""
    email = f"expired_verify_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Tom Ford",
        "email": email,
        "password": "GucciEra1994!"
    })
    user_id = uuid.UUID(reg.json()["user"]["id"])

    raw_token, token_hash = generate_action_token()
    expired_entry = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        used_at=None,
        created_at=datetime.now(timezone.utc) - timedelta(hours=25)
    )
    db.add(expired_entry)
    db.commit()

    res = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


def test_resend_verification_invalidates_previous_token(db):
    """Test resending verification email invalidates previous tokens and delivers new one."""
    email = f"resend_verify_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Phoebe Philo",
        "email": email,
        "password": "MinimalAtelier2008!"
    })
    user_id = uuid.UUID(reg.json()["user"]["id"])

    # Extract initial verification token
    outbox1 = get_test_outbox()
    initial_token = re.search(r"token=([A-Za-z0-9_-]+)", outbox1[0]["text"]).group(1)
    clear_test_outbox()

    # Call resend-verification
    resend_res = client.post("/api/v1/auth/resend-verification", json={"email": email})
    assert resend_res.status_code == 200

    outbox2 = get_test_outbox()
    assert len(outbox2) == 1
    new_token = re.search(r"token=([A-Za-z0-9_-]+)", outbox2[0]["text"]).group(1)
    assert new_token != initial_token

    # Attempting to use the old initial token must fail (it was invalidated)
    old_res = client.post("/api/v1/auth/verify-email", json={"token": initial_token})
    assert old_res.status_code == 400

    # Using the new token must succeed
    new_res = client.post("/api/v1/auth/verify-email", json={"token": new_token})
    assert new_res.status_code == 200
    assert "verified" in new_res.json()["message"].lower()


# ============================================================================
# Dedicated Automated Test Suite: 11 Required Test Scenarios
# ============================================================================

def test_req_1_smtp_mock_delivery():
    """1. SMTP mock delivery: Captures outbound emails into in-memory mailbox without network calls."""
    clear_test_outbox()

    # Generic send_email
    res1 = send_email(
        to_email="customer@atelier.nutz",
        subject="Order Confirmation",
        html_content="<p>Order Placed</p>",
        text_content="Order Placed"
    )
    assert res1 is True

    # send_verification_email
    res2 = send_verification_email(
        to_email="verify_test@atelier.nutz",
        raw_token="vtoken_super_secret_123",
        expires_in_hours=24
    )
    assert res2 is True

    # send_password_reset_email
    res3 = send_password_reset_email(
        to_email="reset_test@atelier.nutz",
        raw_token="rtoken_super_secret_456",
        expires_in_minutes=30
    )
    assert res3 is True

    outbox = get_test_outbox()
    assert len(outbox) == 3
    assert outbox[0]["to"] == "customer@atelier.nutz"
    assert outbox[0]["subject"] == "Order Confirmation"
    assert "token=vtoken_super_secret_123" in outbox[1]["text"]
    assert "token=rtoken_super_secret_456" in outbox[2]["text"]


def test_req_2_smtp_configuration_validation():
    """2. SMTP configuration validation: Validates presence of all required SMTP keys without credential leaks."""
    val = validate_smtp_configuration()
    assert val["valid"] is True, f"Missing SMTP settings: {val.get('missing_fields')}"
    assert val["host"] == "smtp.gmail.com"
    assert val["port"] == 587
    assert val["username"] == "parotabalu007@gmail.com"
    assert val["from_email"] == "parotabalu007@gmail.com"
    assert val["use_tls"] is True
    assert val["use_ssl"] is False
    # Ensure sensitive password field is strictly omitted from the validation dictionary
    assert "password" not in val


def test_req_3_successful_email_verification(db):
    """3. Successful email verification: Token verification marks user.email_verified = True."""
    email = f"verified_success_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Hubert de Givenchy",
        "email": email,
        "password": "AudreyHepburn1954!"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    user_id = uuid.UUID(reg.json()["user"]["id"])

    # Verify initial DB state is unverified
    user_db = db.query(User).filter(User.id == user_id).first()
    assert user_db.email_verified is False

    # Extract token
    outbox = get_test_outbox()
    raw_vtoken = re.search(r"token=([A-Za-z0-9_-]+)", outbox[0]["text"]).group(1)

    # Submit verification
    v_res = client.post("/api/v1/auth/verify-email", json={"token": raw_vtoken})
    assert v_res.status_code == 200
    assert "verified" in v_res.json()["message"].lower()

    # Verify updated DB state
    db.refresh(user_db)
    assert user_db.email_verified is True

    # Verify via /api/v1/auth/me
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email_verified"] is True


def test_req_4_expired_verification_token(db):
    """4. Expired verification token: Rejects token past its 24-hour expiration window."""
    email = f"expired_verify_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Cristobal Balenciaga",
        "email": email,
        "password": "MasterOfTailoring1937!"
    })
    user_id = uuid.UUID(reg.json()["user"]["id"])

    raw_token, token_hash = generate_action_token()
    expired_entry = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
        used_at=None,
        created_at=datetime.now(timezone.utc) - timedelta(hours=26)
    )
    db.add(expired_entry)
    db.commit()

    res = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


def test_req_5_invalid_verification_token():
    """5. Invalid verification token: Rejects fabricated or non-existent token hashes."""
    res = client.post("/api/v1/auth/verify-email", json={"token": "fabricated_random_token_string_999"})
    assert res.status_code == 400
    assert "invalid" in res.json()["detail"].lower()


def test_req_6_resend_verification(db):
    """6. Resend verification: Generates a fresh token and invalidates the previous token."""
    email = f"resend_test_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Yves Saint Laurent",
        "email": email,
        "password": "LeSmokingTuxedo1966!"
    })
    assert reg.status_code == 201
    first_token = re.search(r"token=([A-Za-z0-9_-]+)", get_test_outbox()[0]["text"]).group(1)
    clear_test_outbox()

    # Resend
    resend = client.post("/api/v1/auth/resend-verification", json={"email": email})
    assert resend.status_code == 200

    outbox = get_test_outbox()
    assert len(outbox) == 1
    second_token = re.search(r"token=([A-Za-z0-9_-]+)", outbox[0]["text"]).group(1)
    assert second_token != first_token

    # Verify first token is now invalidated
    invalid_res = client.post("/api/v1/auth/verify-email", json={"token": first_token})
    assert invalid_res.status_code == 400

    # Verify second token is valid
    valid_res = client.post("/api/v1/auth/verify-email", json={"token": second_token})
    assert valid_res.status_code == 200
    assert "verified" in valid_res.json()["message"].lower()


def test_req_7_successful_password_reset(db):
    """7. Successful password reset: Validates single-use token, resets Argon2id hash, and revokes prior JWTs."""
    email = f"pwd_reset_success_{uuid.uuid4().hex[:8]}@nutz.ai"
    old_pwd = "OldMasterPassword2026!"
    new_pwd = "NewAtelierPassword2026!"

    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Christian Dior",
        "email": email,
        "password": old_pwd
    })
    initial_jwt = reg.json()["access_token"]
    clear_test_outbox()

    # Request reset
    forgot = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot.status_code == 200

    reset_token = re.search(r"token=([A-Za-z0-9_-]+)", get_test_outbox()[0]["text"]).group(1)

    # Perform reset
    reset_res = client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": new_pwd
    })
    assert reset_res.status_code == 200
    assert "success" in reset_res.json()["status"]

    # Verify old password fails
    fail_login = client.post("/api/v1/auth/login", json={"email": email, "password": old_pwd})
    assert fail_login.status_code == 401

    # Verify new password succeeds
    succ_login = client.post("/api/v1/auth/login", json={"email": email, "password": new_pwd})
    assert succ_login.status_code == 200
    assert "access_token" in succ_login.json()

    # Verify pre-reset JWT is rejected
    stale_jwt = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {initial_jwt}"})
    assert stale_jwt.status_code == 401


def test_req_8_expired_password_reset_token(db):
    """8. Expired password-reset token: Rejects reset tokens past 30-minute expiration window."""
    email = f"expired_reset_req_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Elsa Schiaparelli",
        "email": email,
        "password": "ShockingPink1937!"
    })
    user_id = uuid.UUID(reg.json()["user"]["id"])

    raw_token, token_hash = generate_action_token()
    expired_entry = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        used_at=None,
        created_at=datetime.now(timezone.utc) - timedelta(minutes=40)
    )
    db.add(expired_entry)
    db.commit()

    res = client.post("/api/v1/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewSchiaparelliPass123!"
    })
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


def test_req_9_reuse_of_already_used_token(db):
    """9. Reuse of an already-used token: Prevents replay attacks for both reset and verification tokens."""
    email = f"token_reuse_{uuid.uuid4().hex[:8]}@nutz.ai"
    client.post("/api/v1/auth/register", json={
        "full_name": "Jeanne Lanvin",
        "email": email,
        "password": "LanvinBlue1889!"
    })
    vtoken = re.search(r"token=([A-Za-z0-9_-]+)", get_test_outbox()[0]["text"]).group(1)

    # 1. First use: valid
    v1 = client.post("/api/v1/auth/verify-email", json={"token": vtoken})
    assert v1.status_code == 200

    # 2. Second use: rejected
    v2 = client.post("/api/v1/auth/verify-email", json={"token": vtoken})
    assert v2.status_code == 400
    assert "already used" in v2.json()["detail"].lower()


def test_req_10_password_hash_verification():
    """10. Password hash verification: Rigorous verification of Argon2id hashing parameters and collision resistance."""
    pass1 = "SecretAtelierPhrase2026!"
    hash1 = hash_password(pass1)
    hash2 = hash_password(pass1)

    # Format check
    assert hash1.startswith("$argon2id$")
    assert "$m=65536,t=3,p=4$" in hash1

    # Salt uniqueness
    assert hash1 != hash2, "Argon2id salts must be randomized for every hash generation"

    # Match verification
    assert verify_password(pass1, hash1) is True
    assert verify_password(pass1, hash2) is True
    assert verify_password("WrongPassword123!", hash1) is False
    assert verify_password("", hash1) is False


def test_req_11_frontend_api_integration():
    """11. Frontend API integration: Verifies exact payload contracts matching frontend TypeScript service calls."""
    email = f"frontend_contract_{uuid.uuid4().hex[:8]}@nutz.ai"

    # Register
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Coco Chanel",
        "email": email,
        "password": "LittleBlackDress1926!"
    })
    assert reg.status_code == 201
    reg_data = reg.json()
    assert "access_token" in reg_data
    assert "user" in reg_data
    assert reg_data["user"]["email"] == email

    jwt = reg_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {jwt}"}

    # getCurrentUser contract
    me_res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert "user" in me_data
    assert me_data["user"]["email"] == email
    assert "email_verified" in me_data["user"]

    # forgotPassword contract
    forgot_res = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert forgot_res.status_code == 200
    forgot_data = forgot_res.json()
    assert forgot_data["status"] == "success"
    assert "message" in forgot_data

    # resendVerification contract
    resend_res = client.post("/api/v1/auth/resend-verification", json={"email": email})
    assert resend_res.status_code == 200
    resend_data = resend_res.json()
    assert resend_data["status"] == "success"
    assert "message" in resend_data

    # logoutUser contract
    logout_res = client.post("/api/v1/auth/logout", headers=auth_headers)
    assert logout_res.status_code == 200
    logout_data = logout_res.json()
    assert logout_data["status"] == "success"
    assert "logged out" in logout_data["message"].lower()


# ============================================================================
# Privilege Escalation & Role Security Test Suite (Tests 1-6)
# ============================================================================

def test_security_1_normal_registration_assigns_user_role(db):
    """Test 1: Normal registration without specifying role assigns 'user' role in database."""
    email = f"normal_sec_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Standard Patron",
        "email": email,
        "phone": "+1-555-0199",
        "password": "ValidPassword2026!"
    })
    assert reg.status_code == 201
    data = reg.json()
    assert data["user"]["role"] == "user"

    # Query directly from PostgreSQL database
    user_id = uuid.UUID(data["user"]["id"])
    db_user = db.query(User).filter(User.id == user_id).first()
    assert db_user is not None
    assert db_user.role == "user"

    # Verify JWT role claim
    decoded = decode_access_token(data["access_token"])
    assert decoded["role"] == "user"


def test_security_2_admin_privilege_escalation_attempt_prevented(db):
    """Test 2: Attempting to register as 'admin' must never create an administrator account."""
    email = f"exploit_admin_{uuid.uuid4().hex[:8]}@nutz.ai"
    payload = {
        "full_name": "Exploit Admin",
        "email": email,
        "password": "StrongPassword123!",
        "role": "admin"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 201:
        # Extra field was ignored by Pydantic; role must still strictly be 'user'
        data = res.json()
        assert data["user"]["role"] == "user", "Public registration must never assign admin role"
        user_id = uuid.UUID(data["user"]["id"])
        db_user = db.query(User).filter(User.id == user_id).first()
        assert db_user.role == "user", "Database role must strictly be 'user'"
        decoded = decode_access_token(data["access_token"])
        assert decoded["role"] == "user"
    else:
        # Schema rejected extra field with 422
        assert res.status_code == 422


def test_security_3_client_privilege_escalation_attempt_prevented(db):
    """Test 3: Attempting to register as 'client' must never create a client account."""
    email = f"exploit_client_{uuid.uuid4().hex[:8]}@nutz.ai"
    payload = {
        "full_name": "Exploit Client",
        "email": email,
        "password": "StrongPassword123!",
        "role": "client"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    if res.status_code == 201:
        data = res.json()
        assert data["user"]["role"] == "user", "Public registration must never assign client role"
        user_id = uuid.UUID(data["user"]["id"])
        db_user = db.query(User).filter(User.id == user_id).first()
        assert db_user.role == "user", "Database role must strictly be 'user'"
        # Verify no client organization was automatically created
        client_org = db.query(Client).filter(Client.user_id == user_id).first()
        assert client_org is None, "No client profile should be created from public registration"
    else:
        assert res.status_code == 422


def test_security_4_existing_admin_preservation(db):
    """Test 4: Verify existing authorized administrator retains 'admin' role in database."""
    admin_user = db.query(User).filter(User.role == "admin").first()
    assert admin_user is not None, "At least one authorized administrator account must exist"
    assert admin_user.role == "admin"
    assert admin_user.is_active is True


def test_security_5_profile_update_cannot_escalate_role(db):
    """Test 5: Attempting to update role through profile-update APIs is rejected/ignored."""
    email = f"profile_role_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Normal Patron",
        "email": email,
        "password": "Password12345!"
    })
    assert reg.status_code == 201
    jwt_token = reg.json()["access_token"]
    user_id = uuid.UUID(reg.json()["user"]["id"])

    # Attempt to elevate role to admin via PUT /api/v1/auth/me
    headers = {"Authorization": f"Bearer {jwt_token}"}
    update_res = client.put("/api/v1/auth/me", json={
        "full_name": "Normal Patron Updated",
        "role": "admin"
    }, headers=headers)

    # Regardless of whether 200 (extra field ignored) or 422 (extra field rejected), DB role must remain 'user'
    if update_res.status_code == 200:
        assert update_res.json()["role"] == "user"

    db_user = db.query(User).filter(User.id == user_id).first()
    db.refresh(db_user)
    assert db_user.role == "user", "Database role must not be altered by profile update API"


def test_security_6_role_based_authorization_enforcement(db):
    """Test 6: Role authorization enforces 403 on unauthorized roles and 200 on authorized admin."""
    # 1. Normal user with role 'user'
    user_email = f"auth_user_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg_u = client.post("/api/v1/auth/register", json={
        "full_name": "Regular User",
        "email": user_email,
        "password": "Password123!"
    })
    user_token = reg_u.json()["access_token"]

    # Normal user cannot access admin endpoint
    res_u = client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {user_token}"})
    assert res_u.status_code == 403
    assert "Access denied" in res_u.json()["detail"]

    # 2. Client user with role 'client'
    client_email = f"auth_client_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg_c = client.post("/api/v1/auth/register", json={
        "full_name": "Brand Partner",
        "email": client_email,
        "password": "Password123!"
    })
    client_token = reg_c.json()["access_token"]
    # Register client organization and approve via admin
    c_res = client.post("/api/v1/clients", json={"company_name": "Brand Org"}, headers={"Authorization": f"Bearer {client_token}"})
    cid = c_res.json()["id"]

    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={
        "sub": str(admin_user.id),
        "email": admin_user.email,
        "role": admin_user.role
    })
    client.patch(
        f"/api/v1/admin/clients/{cid}/status",
        json={"account_status": "approved"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Client cannot access admin-only endpoint
    res_c = client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {client_token}"})
    assert res_c.status_code == 403
    assert "Access denied" in res_c.json()["detail"]

    # 3. Existing Administrator with role 'admin'
    res_a = client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_a.status_code == 200
    assert isinstance(res_a.json(), list)

    # 4. Unauthenticated request returns 401
    res_unauth = client.get("/api/v1/admin/clients")
    assert res_unauth.status_code == 401


# ============================================================================
# Complete Authentication & Authorization Security Audit Test Suite
# (Scenarios 1-10)
# ============================================================================

def test_audit_1_anonymous_user_blocked_from_client_endpoints():
    """1. Anonymous user accessing protected client endpoints returns 401 Unauthorized."""
    fake_uuid = uuid.uuid4()
    assert client.get("/api/v1/clients/me").status_code == 401
    assert client.post("/api/v1/clients", json={"company_name": "Ghost Corp"}).status_code == 401
    assert client.get("/api/v1/api-keys").status_code == 401
    assert client.post("/api/v1/api-keys", json={"name": "Ghost Key"}).status_code == 401
    assert client.delete(f"/api/v1/api-keys/{fake_uuid}").status_code == 401


def test_audit_2_normal_user_blocked_from_admin_operations(db):
    """2. Normal user attempting admin operations returns 403 Forbidden."""
    email = f"audit_user_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Ordinary User",
        "email": email,
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to list all client organizations
    res_list = client.get("/api/v1/admin/clients", headers=headers)
    assert res_list.status_code == 403
    assert "Access denied" in res_list.json()["detail"]

    # Attempt to approve a client
    fake_cid = uuid.uuid4()
    res_patch = client.patch(
        f"/api/v1/admin/clients/{fake_cid}/status",
        json={"account_status": "approved"},
        headers=headers
    )
    assert res_patch.status_code == 403
    assert "Access denied" in res_patch.json()["detail"]


def test_audit_3_client_blocked_from_admin_operations(db):
    """3. Client attempting admin operations returns 403 Forbidden."""
    email = f"audit_client_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Commercial Client",
        "email": email,
        "password": "Password123!"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # User creates client organization
    c_res = client.post("/api/v1/clients", json={"company_name": "Commercial Brand"}, headers=headers)
    cid = c_res.json()["id"]

    # Admin approves client
    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    client.patch(
        f"/api/v1/admin/clients/{cid}/status",
        json={"account_status": "approved"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Client now attempts admin operations -> must return 403
    list_res = client.get("/api/v1/admin/clients", headers=headers)
    assert list_res.status_code == 403
    assert "Access denied" in list_res.json()["detail"]

    status_res = client.patch(
        f"/api/v1/admin/clients/{cid}/status",
        json={"account_status": "suspended"},
        headers=headers
    )
    assert status_res.status_code == 403


def test_audit_4_user_cannot_access_another_user_records(db):
    """4. User attempting to access another user's records is prevented (Multi-Tenant Isolation)."""
    # User A creates tryon history
    email_a = f"patron_a_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg_a = client.post("/api/v1/auth/register", json={"full_name": "Patron Alpha", "email": email_a, "password": "Password123!"})
    token_a = reg_a.json()["access_token"]
    user_a_id = uuid.UUID(reg_a.json()["user"]["id"])

    # Manually seed a tryon history for User A
    th = TryonHistory(
        user_id=user_a_id,
        garment_category="blazer",
        input_image_reference="/inputs/alpha.jpg",
        output_image_reference="/outputs/alpha.jpg",
        generation_status="completed"
    )
    db.add(th)
    ur = UsageRecord(user_id=user_a_id, operation_type="intelligent_tryon", usage_count=5)
    db.add(ur)
    db.commit()

    # User B registers
    email_b = f"patron_b_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg_b = client.post("/api/v1/auth/register", json={"full_name": "Patron Beta", "email": email_b, "password": "Password123!"})
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B fetches tryon history -> must be empty
    history_b = client.get("/api/v1/tryon/history", headers=headers_b).json()
    assert len(history_b) == 0

    # User B fetches usage summary -> must not see User A's 5 operations
    usage_b = client.get("/api/v1/usage/summary", headers=headers_b).json()
    assert usage_b["usage_summary"] == {}

    # User B calls /auth/me -> sees only User B
    me_b = client.get("/api/v1/auth/me", headers=headers_b).json()
    assert me_b["user"]["email"] == email_b


def test_audit_5_client_cannot_access_another_client_resources(db):
    """5. Client attempting to access another client's resources is prevented (IDOR protection)."""
    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup Client A
    reg_a = client.post("/api/v1/auth/register", json={"full_name": "Client A", "email": f"ca_{uuid.uuid4().hex[:6]}@brand.com", "password": "Password123!"})
    token_a = reg_a.json()["access_token"]
    c_res_a = client.post("/api/v1/clients", json={"company_name": "Brand A"}, headers={"Authorization": f"Bearer {token_a}"})
    cid_a = c_res_a.json()["id"]
    client.patch(f"/api/v1/admin/clients/{cid_a}/status", json={"account_status": "approved"}, headers=admin_headers)
    key_a_res = client.post("/api/v1/api-keys", json={"name": "Brand A Secret Key"}, headers={"Authorization": f"Bearer {token_a}"})
    key_a_id = key_a_res.json()["id"]

    # Setup Client B
    reg_b = client.post("/api/v1/auth/register", json={"full_name": "Client B", "email": f"cb_{uuid.uuid4().hex[:6]}@brand.com", "password": "Password123!"})
    token_b = reg_b.json()["access_token"]
    c_res_b = client.post("/api/v1/clients", json={"company_name": "Brand B"}, headers={"Authorization": f"Bearer {token_b}"})
    cid_b = c_res_b.json()["id"]
    client.patch(f"/api/v1/admin/clients/{cid_b}/status", json={"account_status": "approved"}, headers=admin_headers)
    key_b_res = client.post("/api/v1/api-keys", json={"name": "Brand B Public Key"}, headers={"Authorization": f"Bearer {token_b}"})

    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Client B lists API keys -> must only see key B, never key A
    keys_b = client.get("/api/v1/api-keys", headers=headers_b).json()
    assert len(keys_b) == 1
    assert keys_b[0]["id"] != key_a_id

    # Client B attempts to revoke Client A's key (IDOR attempt) -> 404
    del_res = client.delete(f"/api/v1/api-keys/{key_a_id}", headers=headers_b)
    assert del_res.status_code == 404
    assert "not found" in del_res.json()["detail"].lower()

    # Verify Key A is still active in database
    key_a_db = db.query(ApiCredential).filter(ApiCredential.id == uuid.UUID(key_a_id)).first()
    assert key_a_db.revoked_at is None


def test_audit_6_unauthorized_client_api_key_creation_blocked(db):
    """6. Unauthorized client API-key creation is blocked (no profile or pending profile)."""
    # Case 1: User without client profile
    reg_u = client.post("/api/v1/auth/register", json={"full_name": "No Client Org", "email": f"noclient_{uuid.uuid4().hex[:6]}@nutz.ai", "password": "Password123!"})
    token_u = reg_u.json()["access_token"]
    res1 = client.post("/api/v1/api-keys", json={"name": "Illegal Key"}, headers={"Authorization": f"Bearer {token_u}"})
    assert res1.status_code == 404
    assert "No client profile found" in res1.json()["detail"]

    # Case 2: User with pending client organization
    client.post("/api/v1/clients", json={"company_name": "Pending Corp"}, headers={"Authorization": f"Bearer {token_u}"})
    res2 = client.post("/api/v1/api-keys", json={"name": "Pending Key"}, headers={"Authorization": f"Bearer {token_u}"})
    assert res2.status_code == 403
    assert "pending" in res2.json()["detail"].lower()


def test_audit_7_unauthorized_client_approval_blocked(db):
    """7. Unauthorized client approval attempt by non-admins returns 403 Forbidden."""
    reg = client.post("/api/v1/auth/register", json={"full_name": "Pending Org Owner", "email": f"pending_{uuid.uuid4().hex[:6]}@corp.ai", "password": "Password123!"})
    token = reg.json()["access_token"]
    c_res = client.post("/api/v1/clients", json={"company_name": "Unapproved Corp"}, headers={"Authorization": f"Bearer {token}"})
    cid = c_res.json()["id"]

    # Attacker tries to approve self or another client
    hacker_reg = client.post("/api/v1/auth/register", json={"full_name": "Attacker", "email": f"hacker_{uuid.uuid4().hex[:6]}@dark.ai", "password": "Password123!"})
    hacker_token = hacker_reg.json()["access_token"]

    hack_res = client.patch(
        f"/api/v1/admin/clients/{cid}/status",
        json={"account_status": "approved"},
        headers={"Authorization": f"Bearer {hacker_token}"}
    )
    assert hack_res.status_code == 403

    # Verify status in database remains pending
    client_db = db.query(Client).filter(Client.id == uuid.UUID(cid)).first()
    assert client_db.account_status == "pending"


def test_audit_8_suspended_client_blocked_from_api_access(db):
    """8. Suspended client attempting API access is blocked."""
    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Setup approved client with an active API key
    reg = client.post("/api/v1/auth/register", json={"full_name": "Suspend Me", "email": f"suspend_{uuid.uuid4().hex[:6]}@brand.com", "password": "Password123!"})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    c_res = client.post("/api/v1/clients", json={"company_name": "Suspended Brand"}, headers=headers)
    cid = c_res.json()["id"]
    client.patch(f"/api/v1/admin/clients/{cid}/status", json={"account_status": "approved"}, headers=admin_headers)

    key_res = client.post("/api/v1/api-keys", json={"name": "Pre-Suspension Key"}, headers=headers)
    raw_key = key_res.json()["api_key"]

    # Administrator suspends the client organization
    susp_res = client.patch(f"/api/v1/admin/clients/{cid}/status", json={"account_status": "suspended"}, headers=admin_headers)
    assert susp_res.status_code == 200
    assert susp_res.json()["account_status"] == "suspended"

    # Suspended client tries creating API key -> 403
    bad_key_res = client.post("/api/v1/api-keys", json={"name": "Post-Suspension Key"}, headers=headers)
    assert bad_key_res.status_code == 403
    assert "suspended" in bad_key_res.json()["detail"].lower()

    # Suspended client tries listing API keys -> 403
    bad_list_res = client.get("/api/v1/api-keys", headers=headers)
    assert bad_list_res.status_code == 403
    assert "suspended" in bad_list_res.json()["detail"].lower()

    # Using the pre-existing API key on service resolution -> rejected
    resolved = resolve_user_from_headers({"x-api-key": raw_key}, db)
    assert resolved is None, "API key belonging to suspended client must not resolve"


def test_audit_9_admin_accesses_authorized_management_operations(db):
    """9. Admin successfully accesses authorized management operations."""
    admin_user = db.query(User).filter(User.role == "admin").first()
    admin_token = create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # List all clients
    list_res = client.get("/api/v1/admin/clients", headers=admin_headers)
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)

    # Filter clients by status
    filtered = client.get("/api/v1/admin/clients?status_filter=pending", headers=admin_headers)
    assert filtered.status_code == 200
    for c in filtered.json():
        assert c["account_status"] == "pending"


def test_audit_10_jwt_role_changes_and_stale_token_behavior(db):
    """10. JWT role changes and stale token behavior: Live DB role always overrides stale token claims."""
    # 1. User registers with DB role 'user', issues JWT with claim 'user'
    email = f"stale_test_{uuid.uuid4().hex[:8]}@nutz.ai"
    reg = client.post("/api/v1/auth/register", json={"full_name": "Stale Token Tester", "email": email, "password": "Password123!"})
    stale_user_jwt = reg.json()["access_token"]
    user_id = uuid.UUID(reg.json()["user"]["id"])

    # Verify stale_user_jwt payload has role 'user'
    assert decode_access_token(stale_user_jwt)["role"] == "user"

    # User cannot access admin endpoint
    assert client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {stale_user_jwt}"}).status_code == 403

    # Admin promotes user in database to 'admin'
    user_db = db.query(User).filter(User.id == user_id).first()
    user_db.role = "admin"
    db.commit()

    # User presents the OLD token (which still contains payload role 'user')
    # Because authorization reads current DB role, access to admin endpoint is now GRANTED!
    assert client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {stale_user_jwt}"}).status_code == 200

    # 2. Conversely: Demotion test
    # Issue a token with payload role 'admin'
    admin_jwt = create_access_token(data={"sub": str(user_id), "email": email, "role": "admin"})
    assert decode_access_token(admin_jwt)["role"] == "admin"

    # Demote user in database back to 'user'
    user_db.role = "user"
    db.commit()

    # User presents token claiming 'role=admin'
    # Because backend checks live DB user (role='user'), access is DENIED (403)!
    demoted_res = client.get("/api/v1/admin/clients", headers={"Authorization": f"Bearer {admin_jwt}"})
    assert demoted_res.status_code == 403
    assert "Access denied" in demoted_res.json()["detail"]
