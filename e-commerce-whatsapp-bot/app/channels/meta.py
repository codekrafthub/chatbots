"""
app/channels/meta.py — Meta WhatsApp Cloud API Channel
========================================================
All communication with Meta's official WhatsApp Business Cloud API.

Key functions:
    parse_incoming(data)  → extract (phone, text) from webhook JSON
    send_message(phone, text) → POST to graph.facebook.com
    verify_webhook(request)   → echo hub.challenge for one-time setup

Meta webhook payload shape (simplified):
    {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543210",
                        "type": "text",
                        "text": { "body": "Hello" }
                    }]
                }
            }]
        }]
    }

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks
"""

import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


def parse_incoming(request_data: dict) -> tuple:
    """
    Extract the sender's phone number and message text from a Meta webhook payload.

    Handles two message types:
        - text          → plain WhatsApp message
        - interactive   → button_reply or list_reply (from interactive messages)

    Returns:
        (phone_number: str, text: str) on success
        (None, None) if message type is unsupported or payload is malformed
    """
    try:
        value   = request_data["entry"][0]["changes"][0]["value"]
        message = value["messages"][0]

        phone    = message["from"]
        msg_type = message.get("type", "")

        if msg_type == "text":
            text = message["text"]["body"]

        elif msg_type == "interactive":
            itype = message["interactive"]["type"]
            if itype == "button_reply":
                text = message["interactive"]["button_reply"]["title"]
            elif itype == "list_reply":
                text = message["interactive"]["list_reply"]["title"]
            else:
                logger.info(f"[Meta] Unsupported interactive type: {itype}")
                return None, None

        else:
            logger.info(f"[Meta] Unsupported message type: {msg_type} — ignoring")
            return None, None

        return phone, text

    except (KeyError, IndexError, TypeError) as exc:
        logger.error(f"[Meta] Failed to parse webhook payload: {exc}")
        return None, None


def send_message(phone: str, text: str) -> bool:
    """
    Send a plain-text WhatsApp message via the Meta Cloud API.

    Args:
        phone: Recipient's number in international format, no '+' (e.g. '919876543210')
        text:  Message body (WhatsApp max is 4096 characters)

    Returns:
        True on HTTP 2xx, False on any error.
    """
    api_version      = current_app.config["META_API_VERSION"]
    phone_number_id  = current_app.config["META_PHONE_NUMBER_ID"]
    access_token     = current_app.config["META_ACCESS_TOKEN"]

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to":   phone,
        "type": "text",
        "text": {"body": text},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info(f"[Meta] ✅ Message sent to {phone}")
        return True

    except requests.RequestException as exc:
        logger.error(f"[Meta] ❌ Send failed to {phone}: {exc}")
        return False


def verify_webhook(request) -> tuple:
    """
    Handle the one-time GET request Meta sends when you save a webhook URL
    in the Meta Developer Portal.

    Meta sends: ?hub.mode=subscribe&hub.verify_token=<token>&hub.challenge=<string>
    We must return hub.challenge with HTTP 200 if the token matches.

    Returns:
        (response_body, http_status_code)
    """
    mode      = request.args.get("hub.mode")
    token     = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    expected_token = current_app.config["META_VERIFY_TOKEN"]

    if mode == "subscribe" and token == expected_token:
        logger.info("[Meta] ✅ Webhook verified successfully")
        return challenge, 200

    logger.warning("[Meta] ❌ Webhook verification failed — token mismatch")
    return "Forbidden", 403
