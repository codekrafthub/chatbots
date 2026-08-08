from __future__ import annotations

import uuid

from flask import Blueprint, jsonify, render_template, request, session

from ..services.bot import process_incoming_message

public_bp = Blueprint("public", __name__)


@public_bp.get("/")
def index():
    return render_template("public/index.html")


@public_bp.get("/demo")
def demo():
    session.setdefault("demo_phone", f"demo:{uuid.uuid4().hex[:10]}")
    return render_template("public/demo.html", demo_phone=session["demo_phone"])


@public_bp.post("/api/demo/message")
def demo_message():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("message") or "").strip()
    phone = payload.get("phone") or session.setdefault("demo_phone", f"demo:{uuid.uuid4().hex[:10]}")
    reply = process_incoming_message(phone=phone, text=text, channel="demo", profile_name="Demo User")
    return jsonify({"reply": reply})


@public_bp.get("/health")
def health():
    return jsonify({"status": "ok"})
