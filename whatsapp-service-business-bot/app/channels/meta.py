from __future__ import annotations

import requests
from flask import current_app


def extract_meta_message(payload: dict) -> dict | None:
    """
    Extract useful information from a Meta WhatsApp webhook payload.

    Returns:
        dict containing sender information and message text,
        or None if the payload is invalid.
    """
    try:
        value = payload["entry"][0]["changes"][0]["value"]
        message = value.get("messages", [None])[0]

        if not message:
            return None

        contact = value.get("contacts", [{}])[0]

        return {
            "from": message.get("from"),
            "text": message.get("text", {}).get("body", ""),
            "message_id": message.get("id"),
            "profile_name": contact.get("profile", {}).get("name"),
            "raw": payload,
        }

    except (KeyError, IndexError, TypeError):
        current_app.logger.warning("Invalid Meta webhook payload received.")
        return None


def send_meta_text(to_phone: str, text: str) -> bool:
    """
    Send a WhatsApp text message using Meta Cloud API.
    """

    token = current_app.config.get("META_ACCESS_TOKEN")
    phone_number_id = current_app.config.get("META_PHONE_NUMBER_ID")
    version = current_app.config.get("META_GRAPH_API_VERSION", "v25.0")

    if not token or not phone_number_id:
        current_app.logger.info(
            "META credentials not configured. Reply generated but not sent: %s",
            text,
        )
        return False

    # WhatsApp Cloud API allows a maximum of 4000 characters.
    if len(text) > 4000:
        current_app.logger.warning(
            f"Message truncated to 4000 chars from {len(text)} chars"
        )

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text[:4000],
        },
    }

    url = (
        f"https://graph.facebook.com/"
        f"{version}/{phone_number_id}/messages"
    )

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=15,
        )

        if response.status_code >= 400:
            current_app.logger.error(
                "Meta send failed (%s): %s",
                response.status_code,
                response.text,
            )
            return False

        return True

    except requests.RequestException as exc:
        current_app.logger.exception(
            "Unable to send Meta message: %s",
            exc,
        )
        return False