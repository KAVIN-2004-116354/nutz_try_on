# NUTZ Virtual Fitting Room - Authentication & Identity Documentation

## 1. Overview

The Nutz Try-On authentication and user management system is built for production SaaS operations, combining:
- **Argon2id password hashing** via `argon2-cffi` (type `ID`, `time_cost=3`, `memory_cost=65536`, `parallelism=4`).
- **Cryptographically signed JWT sessions** via PyJWT with guaranteed `jti` (JWT ID), `sub`, `exp`, and `iat` claims.
- **Server-side JWT revocation** using PostgreSQL table `revoked_tokens` for secure instant logout.
- **Session invalidation on password change** using `password_changed_at` timestamp comparison.
- **Single-use, time-limited token hashing** (SHA-256) for Password Resets (30 min) and Email Verifications (24 hr).
- **Anti-enumeration and rate-limiting** protections across forgot-password and verification endpoints.

---

## 2. API Endpoints

### 2.1 Secure Logout
- **Endpoint**: `POST /api/v1/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Description**: Identifies active user, extracts the token's `jti` claim, records it in `revoked_tokens` in PostgreSQL with its expiration timestamp, and isolates revocation to the caller. Handles expired tokens gracefully and idempotently.
- **Response**:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

### 2.2 Forgot Password
- **Endpoint**: `POST /api/v1/auth/forgot-password`
- **Body**:
```json
{
  "email": "user@example.com"
}
```
- **Description**: Generates a high-entropy cryptographically secure random token, stores its SHA-256 hash in PostgreSQL (`password_reset_tokens`) with a 30-minute expiration, and delivers the reset link (`${FRONTEND_URL}/reset-password?token=<raw_token>`).
- **Security**:
  - Always returns the same generic message whether the email exists or not to prevent account enumeration.
  - Rate limited (max 4 requests per 10 minutes per IP/email).
  - Raw token is never returned in HTTP responses or stored in logs.
- **Response**:
```json
{
  "status": "success",
  "message": "If this email is registered, password reset instructions have been sent."
}
```

### 2.3 Reset Password
- **Endpoint**: `POST /api/v1/auth/reset-password`
- **Body**:
```json
{
  "token": "secret_reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}
```
- **Description**: Computes SHA-256 hash of token, verifies it is unexpired and unused, hashes the new password using Argon2id, marks token as used, and invalidates all existing JWT sessions by updating `users.password_changed_at`.
- **Response**:
```json
{
  "status": "success",
  "message": "Password has been successfully reset. Please sign in with your new password."
}
```

### 2.4 Verify Email
- **Endpoint**: `POST /api/v1/auth/verify-email`
- **Body**:
```json
{
  "token": "verification_token_from_email"
}
```
- **Description**: Validates verification token hash against `email_verification_tokens`, verifies expiration (24 hours), updates `users.email_verified = TRUE`, and marks token as used.
- **Response**:
```json
{
  "status": "success",
  "message": "Email address has been successfully verified."
}
```

### 2.5 Resend Verification Email
- **Endpoint**: `POST /api/v1/auth/resend-verification`
- **Body**:
```json
{
  "email": "user@example.com"
}
```
- **Description**: Invalidates prior unused verification tokens for the user, generates a new token and hash, sends a fresh email, and applies rate limiting. Returns generic message to prevent account enumeration.
- **Response**:
```json
{
  "status": "success",
  "message": "If this email is associated with an unverified account, a new verification link has been sent."
}
```

---

## 3. SMTP Email Configuration

Configure your SMTP credentials in `.env`:

```bash
SMTP_HOST="smtp.mailtrap.io"
SMTP_PORT=587
SMTP_USERNAME="your-username"
SMTP_PASSWORD="your-password"
SMTP_FROM_EMAIL="noreply@nutz.ai"
SMTP_FROM_NAME="NUTZ Virtual Fitting Room"
SMTP_USE_TLS=true
SMTP_USE_SSL=false
FRONTEND_URL="http://localhost:5173"
```

### Local Development / Testing
In local test and CI environments, `is_test_environment()` detects `pytest` or `MOCK_EMAIL=true`, capturing all outgoing emails into an in-memory outbox (`get_test_outbox()`) without making live network calls.

---

## 4. Database Schema Updates

Alembic migrations track the following tables:
1. `revoked_tokens`: `id`, `jti` (unique, indexed), `user_id` (FK cascade), `expires_at`, `revoked_at`, `created_at`.
2. `password_reset_tokens`: `id`, `user_id` (FK cascade), `token_hash` (unique, indexed), `expires_at`, `used_at`, `created_at`.
3. `email_verification_tokens`: `id`, `user_id` (FK cascade), `token_hash` (unique, indexed), `expires_at`, `used_at`, `created_at`.
4. `users.password_changed_at`: Timestamp column to immediately revoke all prior sessions upon password reset.
