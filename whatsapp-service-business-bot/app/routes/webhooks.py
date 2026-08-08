from __future__ import annotations

from flask import Blueprint, abort, current_app, jsonify, request

from ..channels.meta import extract_meta_message, send_meta_text
from ..channels.twilio import twiml_message, validate_twilio_signature
from ..services.bot import process_incoming_message

webhooks_bp = Blueprint("webhooks", __name__, url_prefix="/webhook")


@webhooks_bp.post("/twilio")
def twilio_webhook():
    if not validate_twilio_signature():
        abort(403)
    incoming_text = request.form.get("Body", "")
    from_phone = request.form.get("From", "unknown")
    profile_name = request.form.get("ProfileName") or request.form.get("WaId")
    message_sid = request.form.get("MessageSid")
    reply = process_incoming_message(
        phone=from_phone,
        text=incoming_text,
        channel="twilio",
        profile_name=profile_name,
        external_id=message_sid,
        meta=dict(request.form.items()),
    )
    return twiml_message(reply)


@webhooks_bp.get("/meta")
def meta_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == current_app.config.get("META_VERIFY_TOKEN"):
        return challenge or "", 200
    return "Verification failed", 403


@webhooks_bp.post("/meta")
def meta_webhook():
    payload = request.get_json(silent=True) or {}
    parsed = extract_meta_message(payload)
    if not parsed:
        return jsonify({"ok": True, "ignored": True})
    reply = process_incoming_message(
        phone=parsed["from"],
        text=parsed["text"],
        channel="meta",
        profile_name=parsed.get("profile_name"),
        external_id=parsed.get("message_id"),
        meta=parsed.get("raw"),
    )
    sent = send_meta_text(parsed["from"], reply)
    return jsonify({"ok": True, "sent": sent})
