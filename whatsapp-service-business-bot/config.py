import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = _bool("FLASK_DEBUG", False)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'servicebot.sqlite3'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe@12345")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "Project Admin")

    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Spice Garden Restaurant")
    BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "+91 98765 43210")
    BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "MG Road, Pune, Maharashtra")
    BUSINESS_OPENING_HOURS = os.getenv("BUSINESS_OPENING_HOURS", "Mon-Sun 10:00 AM - 11:00 PM")
    BUSINESS_CURRENCY = os.getenv("BUSINESS_CURRENCY", "INR")
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    VALIDATE_TWILIO_SIGNATURE = _bool("VALIDATE_TWILIO_SIGNATURE", False)

    META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "change-this-verify-token")
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
    META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID", "")
    META_GRAPH_API_VERSION = os.getenv("META_GRAPH_API_VERSION", "v25.0")

    LOAD_DEMO_ANALYTICS = _bool("LOAD_DEMO_ANALYTICS", True)
