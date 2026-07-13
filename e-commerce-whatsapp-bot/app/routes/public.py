"""
app/routes/public.py — Public-Facing Routes
============================================
Serves the two public pages:

    /        → Landing page showcasing the bot's features
    /demo    → Interactive in-browser bot demo (AJAX to /api/demo/chat)
    /api/demo/chat → JSON endpoint powering the demo widget
"""

import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services.bot import handle_message

logger = logging.getLogger(__name__)

public_bp = Blueprint("public", __name__)


@public_bp.get("/")
def index():
    """Marketing landing page for the WhatsApp e-commerce bot."""
    return render_template(
        "public/index.html",
        store_name=current_app.config["STORE_NAME"],
        bot_name=current_app.config["BOT_NAME"],
    )


@public_bp.get("/demo")
def demo():
    """
    Interactive bot demo page.
    Users type messages in a mock WhatsApp UI; AJAX sends them to /api/demo/chat.
    """
    return render_template(
        "public/demo.html",
        bot_name=current_app.config["BOT_NAME"],
        store_name=current_app.config["STORE_NAME"],
    )


@public_bp.post("/api/demo/chat")
def demo_chat():
    """
    JSON API endpoint for the browser-based demo.
    Accepts { "message": "...", "phone": "demo_user" }
    Returns  { "reply": "..." }

    Uses a fixed demo phone so it doesn't pollute real lead data.
    """
    body    = request.get_json(silent=True) or {}
    text    = (body.get("message") or "").strip()
    # Use a demo phone number so it's separate from real leads
    phone   = body.get("phone", "demo_+910000000000")

    if not text:
        return jsonify({"reply": "Please type a message."}), 400

    try:
        reply = handle_message(phone=phone, text=text, channel="demo")
        return jsonify({"reply": reply})
    except Exception as exc:
        logger.error(f"[Demo] Error processing message: {exc}", exc_info=True)
        return jsonify({"reply": "Something went wrong. Please try again."}), 500