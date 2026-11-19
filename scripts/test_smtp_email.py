#!/usr/bin/env python3
"""
NUTZ Virtual Fitting Room - SMTP Email Verification Test Script
---------------------------------------------------------------
Tests live email delivery through configured SMTP settings using send_email().
Accepts recipient email address via CLI arguments.
Never outputs passwords, secrets, or sensitive tokens.
"""

import sys
import os
import argparse
import time
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.email_service import (
    send_email,
    get_smtp_settings,
    validate_smtp_configuration,
)


def mask_username(username: str) -> str:
    """Masks username/email for safe display without leaking full identity."""
    if "@" in username:
        user, domain = username.split("@", 1)
        if len(user) <= 3:
            return f"{user[0]}***@{domain}"
        return f"{user[:2]}***{user[-1]}@{domain}"
    if len(username) <= 4:
        return "****"
    return f"{username[:2]}***{username[-2:]}"


def main():
    parser = argparse.ArgumentParser(
        description="Verify SMTP configuration and test live email delivery in NUTZ Try-On."
    )
    parser.add_argument(
        "recipient_positional",
        nargs="?",
        default=None,
        help="Recipient email address (optional if --to is provided)"
    )
    parser.add_argument(
        "--to",
        "-t",
        dest="recipient_flag",
        default=None,
        help="Recipient email address"
    )

    args = parser.parse_args()
    recipient = args.recipient_flag or args.recipient_positional

    if not recipient:
        print("[ERROR] Recipient email is required.")
        print("Usage: python scripts/test_smtp_email.py <recipient_email>")
        print("   or: python scripts/test_smtp_email.py --to <recipient_email>")
        sys.exit(1)

    recipient = recipient.strip()
    if "@" not in recipient or "." not in recipient:
        print(f"[ERROR] Invalid recipient email address: '{recipient}'")
        sys.exit(1)

    # 1. Validate SMTP Configuration
    validation = validate_smtp_configuration()
    if not validation["valid"]:
        print("[ERROR] Incomplete SMTP configuration!")
        print(f"Missing required fields: {', '.join(validation['missing_fields'])}")
        print("Please check your .env file.")
        sys.exit(1)

    settings = get_smtp_settings()
    masked_user = mask_username(settings["username"])

    print("====================================================================")
    print("      NUTZ VIRTUAL FITTING ROOM - SMTP EMAIL DELIVERY TEST         ")
    print("====================================================================")
    print(f"SMTP Host:       {settings['host']}")
    print(f"SMTP Port:       {settings['port']}")
    print(f"SMTP Username:   {masked_user}")
    print(f"SMTP From:       {settings['from_name']} <{settings['from_email']}>")
    print(f"Security:        TLS={settings['use_tls']}, SSL={settings['use_ssl']}")
    print(f"Recipient:       {recipient}")
    print(f"Timestamp (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("====================================================================")
    print(f"[*] Dispatching test verification email to {recipient}...")

    subject = "NUTZ Atelier - SMTP Verification Test"
    text_content = f"""NUTZ Atelier - Virtual Fitting Room
SMTP Verification Test

This is an automated test verifying Gmail SMTP delivery for NUTZ Virtual Fitting Room.
Timestamp: {datetime.now(timezone.utc).isoformat()}
Recipient: {recipient}
Host: {settings['host']}:{settings['port']}

If you received this message, the email delivery pipeline is verified and operational.
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #FAF9F6; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 24px; border: 1px solid #EAE7E0; padding: 40px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }}
    h1 {{ font-family: Georgia, serif; color: #171717; font-size: 24px; margin-bottom: 12px; }}
    p {{ color: #555555; font-size: 14px; line-height: 1.6; }}
    .badge {{ display: inline-block; background: #ECFDF5; color: #065F46; padding: 10px 20px; border-radius: 999px; font-weight: 600; font-size: 13px; margin: 20px 0; border: 1px solid #A7F3D0; }}
    .meta {{ background: #F8F7F4; border-radius: 12px; padding: 16px; font-family: monospace; font-size: 12px; color: #4B5563; text-align: left; margin: 20px 0; }}
    .footer {{ font-size: 11px; color: #9CA3AF; margin-top: 30px; border-top: 1px solid #EAE7E0; padding-top: 20px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>NUTZ Atelier Delivery Verified</h1>
    <div class="badge">&#10003; SMTP Service Operational</div>
    <p>This automated message confirms that Gmail SMTP transport is active, authenticated, and capable of dispatching authentication and security emails.</p>
    <div class="meta">
      <strong>Host:</strong> {settings['host']}:{settings['port']}<br>
      <strong>Sender:</strong> {settings['from_name']}<br>
      <strong>Recipient:</strong> {recipient}<br>
      <strong>Timestamp:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
      <strong>Status:</strong> Active & Verified
    </div>
    <div class="footer">
      NUTZ AI Fashion Technologies &bull; Pure Cloud FLUX.1 Dev Dressing Studio
    </div>
  </div>
</body>
</html>
"""

    start_time = time.time()
    try:
        # Call send_email with force_live=True to trigger real SMTP socket delivery
        success = send_email(
            to_email=recipient,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            force_live=True
        )
        elapsed = time.time() - start_time

        if success:
            print(f"[SUCCESS] Email successfully delivered to {recipient} in {elapsed:.2f}s!")
            print("[INFO] Gmail SMTP integration is fully functional and ready for production authentication flows.")
            sys.exit(0)
        else:
            print(f"[FAILURE] send_email() returned False without raising an exception.")
            sys.exit(1)

    except Exception as exc:
        elapsed = time.time() - start_time
        print(f"[FAILURE] SMTP delivery failed after {elapsed:.2f}s: {type(exc).__name__}")
        print(f"[DETAILS] {str(exc)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
