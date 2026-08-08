from __future__ import annotations

from xml.sax.saxutils import escape

from flask import Response, current_app, request


def twiml_message(body: str) -> Response:
    """
    Generate a valid TwiML XML response.
    """
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(body)}</Message></Response>"
    )
    return Response(xml, mimetype="application/xml")


def validate_twilio_signature() -> bool:
    """
    Validate incoming Twilio webhook requests.

    Signature validation is strongly recommended in production.
    It may be disabled only for local development/testing.
    """

    validate = current_app.config.get("VALIDATE_TWILIO_SIGNATURE", True)

    if not validate:
        current_app.logger.warning(
            "Twilio signature validation is DISABLED. "
            "Use this only during local development."
        )
        return True

    token = current_app.config.get("TWILIO_AUTH_TOKEN")

    if not token:
        current_app.logger.error(
            "Twilio Auth Token is missing. Signature validation failed."
        )
        return False

    try:
        from twilio.request_validator import RequestValidator
    except ImportError:
        current_app.logger.error(
            "Twilio package is not installed. "
            "Cannot validate webhook signature."
        )
        return False

    validator = RequestValidator(token)

    signature = request.headers.get("X-Twilio-Signature", "")

    public_base = current_app.config.get("PUBLIC_BASE_URL", "").rstrip("/")

    url = (
        f"{public_base}{request.path}"
        if public_base
        else request.url
    )

    try:
        valid = validator.validate(
            url,
            request.form,
            signature,
        )

        if not valid:
            current_app.logger.warning(
                "Invalid Twilio webhook signature."
            )

        return valid

    except Exception as exc:
        current_app.logger.exception(
            "Twilio signature validation failed: %s",
            exc,
        )
        return False