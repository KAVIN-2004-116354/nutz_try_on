import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger("nutz.email")


def get_smtp_settings() -> Dict[str, Any]:
    """
    Dynamically loads and sanitizes SMTP configuration from environment.
    Strips inline comments and formats Google App Passwords by removing whitespace.
    """
    raw_host = os.getenv("SMTP_HOST", "localhost").split("#")[0].strip()
    raw_port = os.getenv("SMTP_PORT", "587").split("#")[0].strip()
    raw_user = os.getenv("SMTP_USERNAME", "").split("#")[0].strip()
    raw_pwd = os.getenv("SMTP_PASSWORD", "").split("#")[0].strip()
    raw_from_email = os.getenv("SMTP_FROM_EMAIL", "noreply@nutz.ai").split("#")[0].strip()
    raw_from_name = os.getenv("SMTP_FROM_NAME", "NUTZ Virtual Fitting Room").split("#")[0].strip()
    raw_tls = os.getenv("SMTP_USE_TLS", "true").split("#")[0].strip().lower() in ("true", "1", "yes")
    raw_ssl = os.getenv("SMTP_USE_SSL", "false").split("#")[0].strip().lower() in ("true", "1", "yes")
    raw_frontend = os.getenv("FRONTEND_URL", "http://localhost:5173").split("#")[0].strip().rstrip("/")
    raw_mock = os.getenv("MOCK_EMAIL", "false").split("#")[0].strip().lower() in ("true", "1", "yes")

    # If Google App Password (often formatted with spaces like 'abcd efgh ijkl mnop'), strip spaces
    clean_pwd = raw_pwd
    if "gmail" in raw_host.lower() or " " in clean_pwd:
        clean_pwd = clean_pwd.replace(" ", "")

    return {
        "host": raw_host,
        "port": int(raw_port) if raw_port.isdigit() else 587,
        "username": raw_user,
        "password": clean_pwd,
        "from_email": raw_from_email,
        "from_name": raw_from_name,
        "use_tls": raw_tls,
        "use_ssl": raw_ssl,
        "frontend_url": raw_frontend,
        "mock_email": raw_mock,
    }


# Backwards compatibility constants
SMTP_HOST = os.getenv("SMTP_HOST", "localhost").split("#")[0].strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587").split("#")[0].strip()) if os.getenv("SMTP_PORT", "587").split("#")[0].strip().isdigit() else 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").split("#")[0].strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").split("#")[0].strip().replace(" ", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@nutz.ai").split("#")[0].strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "NUTZ Virtual Fitting Room").split("#")[0].strip()
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").split("#")[0].strip().lower() in ("true", "1", "yes")
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").split("#")[0].strip().lower() in ("true", "1", "yes")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").split("#")[0].strip().rstrip("/")

# In-memory test mailbox for unit testing
_test_outbox: List[Dict[str, Any]] = []


def get_test_outbox() -> List[Dict[str, Any]]:
    """Returns the in-memory mailbox for test verification."""
    return _test_outbox


def clear_test_outbox() -> None:
    """Clears the test mailbox."""
    _test_outbox.clear()


def is_test_environment() -> bool:
    """Checks if running in pytest or mock environment."""
    if os.getenv("PYTEST_CURRENT_TEST") is not None:
        return True
    mock_val = os.getenv("MOCK_EMAIL", "false").split("#")[0].strip().lower()
    return mock_val in ("true", "1", "yes")


def validate_smtp_configuration() -> Dict[str, Any]:
    """
    Validates required SMTP settings are present and non-empty.
    Returns status dict without exposing credentials.
    """
    settings = get_smtp_settings()
    required_fields = ["host", "port", "username", "password", "from_email"]
    missing = [f for f in required_fields if not settings.get(f)]
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
        "host": settings["host"],
        "port": settings["port"],
        "username": settings["username"],
        "from_email": settings["from_email"],
        "use_tls": settings["use_tls"],
        "use_ssl": settings["use_ssl"],
    }


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str,
    force_live: bool = False
) -> bool:
    """
    Sends an email using configured SMTP settings.
    In testing environments, captures email into _test_outbox without real network calls,
    unless force_live is True.
    Fails safely and raises RuntimeError if SMTP delivery fails in production.
    Never logs sensitive credentials or tokens.
    """
    clean_to = to_email.strip().lower()

    # Capture in test mailbox if running in testing mode and not forced live
    if not force_live and is_test_environment():
        _test_outbox.append({
            "to": clean_to,
            "subject": subject,
            "html": html_content,
            "text": text_content
        })
        return True

    settings = get_smtp_settings()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings['from_name']} <{settings['from_email']}>"
    msg["To"] = clean_to

    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        if settings["use_ssl"]:
            with smtplib.SMTP_SSL(settings["host"], settings["port"], timeout=20) as server:
                if settings["username"] and settings["password"]:
                    server.login(settings["username"], settings["password"])
                server.sendmail(settings["from_email"], [clean_to], msg.as_string())
        else:
            with smtplib.SMTP(settings["host"], settings["port"], timeout=20) as server:
                if settings["use_tls"]:
                    server.starttls()
                if settings["username"] and settings["password"]:
                    server.login(settings["username"], settings["password"])
                server.sendmail(settings["from_email"], [clean_to], msg.as_string())
        return True
    except Exception as exc:
        # Never log SMTP_PASSWORD or full sensitive payload
        logger.error(f"[Email Service] Failed to send email to recipient domain. Reason: {type(exc).__name__}")
        raise RuntimeError(f"SMTP delivery failed: {type(exc).__name__}") from exc


def send_verification_email(
    to_email: str,
    raw_token: str,
    expires_in_hours: int = 24,
    force_live: bool = False
) -> bool:
    """
    Constructs and sends an Email Verification email with luxury atelier formatting.
    Link points to frontend route: ${FRONTEND_URL}/verify-email?token=<token>
    """
    settings = get_smtp_settings()
    frontend_url = settings["frontend_url"]
    verify_url = f"{frontend_url}/verify-email?token={raw_token}"
    subject = "Verify your NUTZ Atelier Fitting Room Account"

    text_content = f"""Welcome to NUTZ Virtual Fitting Room.

Please verify your email address to confirm your account and access all high-fidelity dressing features.

Verification Link:
{verify_url}

Important: This verification link will expire in {expires_in_hours} hours.
If you did not create an account with NUTZ, please ignore this email.
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #FAF9F6; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 24px; border: 1px solid #EAE7E0; padding: 40px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
    .logo {{ width: 56px; height: 56px; margin: 0 auto 20px; }}
    h1 {{ font-family: Georgia, serif; color: #171717; font-size: 24px; margin-bottom: 12px; font-weight: normal; }}
    p {{ color: #555555; font-size: 14px; line-height: 1.6; margin: 16px 0; }}
    .btn {{ display: inline-block; background: #171717; color: #ffffff !important; padding: 14px 32px; border-radius: 999px; text-decoration: none; font-size: 13px; font-weight: bold; margin: 24px 0; letter-spacing: 0.5px; }}
    .footer {{ font-size: 11px; color: #999999; margin-top: 32px; border-top: 1px solid #EAE7E0; padding-top: 20px; }}
    .expiry {{ background: #F5F4F8; padding: 10px 16px; border-radius: 12px; font-size: 12px; color: #4F46E5; display: inline-block; font-weight: 600; margin: 10px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <img src="{frontend_url}/nutz_acorn_logo.png" alt="NUTZ" width="56" height="56" style="border-radius: 16px;">
    </div>
    <h1>Verify Your Atelier Account</h1>
    <p>Welcome to NUTZ Virtual Fitting Room. Please confirm your email address to activate your account memory and personalized fashion drape history.</p>
    <div>
      <a href="{verify_url}" class="btn">Verify Email Address</a>
    </div>
    <div class="expiry">
      Link expires in {expires_in_hours} hours
    </div>
    <p style="font-size: 12px; color: #777;">If the button does not work, copy and paste this link into your browser:<br><a href="{verify_url}" style="color: #171717; word-break: break-all;">{verify_url}</a></p>
    <div class="footer">
      NUTZ AI Fashion Technologies &bull; Pure Cloud FLUX.1 Dev Dressing Studio<br>
      If you did not request this verification, you can safely disregard this message.
    </div>
  </div>
</body>
</html>
"""
    return send_email(to_email, subject, html_content, text_content, force_live=force_live)


def send_password_reset_email(
    to_email: str,
    raw_token: str,
    expires_in_minutes: int = 30,
    force_live: bool = False
) -> bool:
    """
    Constructs and sends a Password Reset email with luxury atelier formatting.
    Link points to frontend route: ${FRONTEND_URL}/reset-password?token=<token>
    """
    settings = get_smtp_settings()
    frontend_url = settings["frontend_url"]
    reset_url = f"{frontend_url}/reset-password?token={raw_token}"
    subject = "Reset your NUTZ Fitting Room Password"

    text_content = f"""NUTZ Virtual Fitting Room Password Reset

We received a request to reset the password for your NUTZ Atelier account.

Reset your password using the link below:
{reset_url}

Important: This link is single-use and will expire in {expires_in_minutes} minutes.
If you did not request a password reset, no action is needed and your account remains safe.
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #FAF9F6; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 24px; border: 1px solid #EAE7E0; padding: 40px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
    .logo {{ width: 56px; height: 56px; margin: 0 auto 20px; }}
    h1 {{ font-family: Georgia, serif; color: #171717; font-size: 24px; margin-bottom: 12px; font-weight: normal; }}
    p {{ color: #555555; font-size: 14px; line-height: 1.6; margin: 16px 0; }}
    .btn {{ display: inline-block; background: #171717; color: #ffffff !important; padding: 14px 32px; border-radius: 999px; text-decoration: none; font-size: 13px; font-weight: bold; margin: 24px 0; letter-spacing: 0.5px; }}
    .footer {{ font-size: 11px; color: #999999; margin-top: 32px; border-top: 1px solid #EAE7E0; padding-top: 20px; }}
    .expiry {{ background: #FEF3C7; padding: 10px 16px; border-radius: 12px; font-size: 12px; color: #92400E; display: inline-block; font-weight: 600; margin: 10px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <img src="{frontend_url}/nutz_acorn_logo.png" alt="NUTZ" width="56" height="56" style="border-radius: 16px;">
    </div>
    <h1>Password Reset Request</h1>
    <p>We received a request to reset your password for your NUTZ Atelier account. Click the button below to choose a new secure password.</p>
    <div>
      <a href="{reset_url}" class="btn">Reset Password</a>
    </div>
    <div class="expiry">
      Link expires in {expires_in_minutes} minutes &bull; Single-use only
    </div>
    <p style="font-size: 12px; color: #777;">If the button does not work, copy and paste this link into your browser:<br><a href="{reset_url}" style="color: #171717; word-break: break-all;">{reset_url}</a></p>
    <div class="footer">
      NUTZ AI Fashion Technologies &bull; Pure Cloud FLUX.1 Dev Dressing Studio<br>
      If you did not request a password reset, you can safely disregard this message. Your password will not change.
    </div>
  </div>
</body>
</html>
"""
    return send_email(to_email, subject, html_content, text_content, force_live=force_live)
