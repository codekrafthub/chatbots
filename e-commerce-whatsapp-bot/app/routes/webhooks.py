"""
app/routes/webhooks.py — WhatsApp Webhook Endpoints
=====================================================
Registers HTTP endpoints that WhatsApp (via Meta or Twilio) calls
every time a user sends a message to the business number.

Routes:
    GET  /webhook/meta    → one-time verification challenge (Meta only)
    POST /webhook/meta    → incoming messages from Meta Cloud API
    POST /webhook/twilio  → incoming messages from Twilio sandbox

Flow for every incoming message:
    1. Channel adapter parses raw payload → (phone, text)
    2. bot.handle_message() runs the FSM → reply string
    3. Channel adapter sends the reply back to WhatsApp
    4. Return 200 to the platform (required to stop retries)
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.bot import handle_message
from twilio.request_validator import RequestValidator
from flask import abort

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint("webhooks", __name__)


# ─── Meta Cloud API ───────────────────────────────────────────────────────────

@webhooks_bp.get("/meta")
def meta_verify():
    """
    One-time webhook verification.
    Meta sends a GET with hub.challenge — we echo it back if the token matches.
    Configure this URL in: Meta Developer Console → App → WhatsApp → Webhooks.
    """
    from app.channels.meta import verify_webhook
    return verify_webhook(request)


@webhooks_bp.post("/meta")
def meta_receive():
    """
    Receive and process incoming WhatsApp messages from Meta Cloud API.
    We always return HTTP 200; returning anything else causes Meta to retry.
    """
    from app.channels.meta import parse_incoming, send_message

    data = request.get_json(silent=True) or {}
    logger.debug(f"[Meta webhook] payload: {data}")

    phone, text = parse_incoming(data)

    if phone and text:
        logger.info(f"[Meta] Incoming from {phone}: {text!r}")
        reply = handle_message(phone=phone, text=text, channel="meta")
        if reply:
            send_message(phone, reply)

    return jsonify({"status": "ok"}), 200


# ─── Twilio Sandbox ───────────────────────────────────────────────────────────

def _twilio_signature_valid():
    if current_app.testing or not current_app.config.get("TWILIO_VALIDATE_SIGNATURE", True):
        return True
    validator = RequestValidator(current_app.config["TWILIO_AUTH_TOKEN"])
    signature = request.headers.get("X-Twilio-Signature", "")
    url = request.url
    forwarded_proto = request.headers.get("X-Forwarded-Proto")
    if forwarded_proto and url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    return validator.validate(url, request.form, signature)


@webhooks_bp.post("/twilio")
def twilio_receive():
    if not _twilio_signature_valid():
        logger.warning("[Twilio] Signature validation failed - check the webhook URL configured in the Twilio Console matches this server's public URL, and that TWILIO_AUTH_TOKEN matches the Console.")
        abort(403)

    from app.channels.twilio import parse_incoming, send_message
    logger.debug(f"[Twilio webhook] form: {dict(request.form)}")
    phone, text = parse_incoming(request.form)
    if phone and text:
        logger.info(f"[Twilio] Incoming from {phone}: {text!r}")
        reply = handle_message(phone=phone, text=text, channel="twilio")
        if reply:
            send_message(phone, reply)

    return (
        '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        200,
        {"Content-Type": "text/xml"},
    )