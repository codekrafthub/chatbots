"""
app/channels/twilio.py — Twilio WhatsApp Sandbox Channel
==========================================================
Twilio's WhatsApp sandbox is the fastest way to test during development —
no Facebook Business Verification needed.

Key functions:
    parse_incoming(form_data) → extract (phone, text) from Twilio POST form
    send_message(phone, text) → sends via Twilio REST Client
    validate_request(request) → HMAC-SHA1 signature check (optional but recommended)

Twilio POST form shape:
    From = 'whatsapp:+919876543210'
    Body = 'Hello'

Docs: https://www.twilio.com/docs/whatsapp/sandbox
"""

import logging
from flask import current_app
from twilio.rest import Client
from twilio.request_validator import RequestValidator

logger = logging.getLogger(__name__)


def _client() -> Client:
    """Build and return a Twilio REST client from app config."""
    return Client(
        current_app.config["TWILIO_ACCOUNT_SID"],
        current_app.config["TWILIO_AUTH_TOKEN"],
    )


def parse_incoming(form_data) -> tuple:
    """
    Extract phone number and message text from Twilio's webhook POST.

    Twilio prefixes phone numbers with 'whatsapp:' — we strip it so the rest
    of the app deals with clean E.164 numbers (e.g. '+919876543210').

    Args:
        form_data: request.form dict-like object

    Returns:
        (phone: str, text: str)  — phone includes the '+' prefix
    """
    raw_from = form_data.get("From", "")
    phone    = raw_from.replace("whatsapp:", "")   # '+919876543210'
    text     = form_data.get("Body", "").strip()
    return phone, text


def send_message(phone: str, text: str) -> bool:
    """
    Send a WhatsApp message via Twilio.

    Args:
        phone: Recipient number with '+' prefix (e.g. '+919876543210')
        text:  Message body

    Returns:
        True on success, False on error.
    """
    to_number = (
        f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
    )

    try:
        msg = _client().messages.create(
            from_=current_app.config["TWILIO_WHATSAPP_FROM"],
            to=to_number,
            body=text,
        )
        logger.info(f"[Twilio] ✅ Sent to {phone} — SID: {msg.sid}")
        return True

    except Exception as exc:
        logger.error(f"[Twilio] ❌ Send failed to {phone}: {exc}")
        return False


def validate_request(request) -> bool:
    """
    Verify the POST is genuinely from Twilio via HMAC-SHA1 signature.
    Call this inside the webhook route for production security.

    Returns:
        True if valid Twilio request, False otherwise.
    """
    validator = RequestValidator(current_app.config["TWILIO_AUTH_TOKEN"])
    signature = request.headers.get("X-Twilio-Signature", "")
    return validator.validate(request.url, request.form.to_dict(), signature)