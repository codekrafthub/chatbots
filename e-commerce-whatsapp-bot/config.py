"""
config.py — Application Configuration
======================================
Loads all settings from environment variables (via .env in dev, real env in prod).
Three environments: development, production, testing (in-memory DB for pytest).
 
Usage in app factory:
    from config import config_map
    app.config.from_object(config_map[os.getenv('FLASK_ENV', 'default')])
"""
 
import os
import sys
from dotenv import load_dotenv
 
# Loads .env file when running locally; in production env vars are set directly.
load_dotenv()
 
 
class Config:
    """Shared base configuration for all environments."""
 
    # ── Flask core ────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-CHANGE-in-production")
 
    # ── Database (SQLite for dev/test, PostgreSQL URL in production) ─────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///ecommerce_bot.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    # ── WhatsApp channel: 'twilio' (sandbox) or 'meta' (production Cloud API) ─
    CHANNEL = os.environ.get("CHANNEL", "twilio")
 
    # Meta WhatsApp Cloud API
    META_VERIFY_TOKEN    = os.environ.get("META_VERIFY_TOKEN", "my_verify_token")
    META_ACCESS_TOKEN    = os.environ.get("META_ACCESS_TOKEN", "")
    META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID", "")
    META_API_VERSION     = os.environ.get("META_API_VERSION", "v18.0")
 
    # Twilio (used for sandbox testing — free, quick to set up)
    TWILIO_ACCOUNT_SID   = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN    = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_FROM = os.environ.get(
        "TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"
    )
 
    # ── Bot identity ──────────────────────────────────────────────────────────
    BOT_NAME   = os.environ.get("BOT_NAME",   "ShopBot")
    STORE_NAME = os.environ.get("STORE_NAME", "My E-Commerce Store")
 
    # ── Admin dashboard credentials ───────────────────────────────────────────
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
 
    # ── Lead scoring thresholds ───────────────────────────────────────────────
    LEAD_HOT_THRESHOLD  = int(os.environ.get("LEAD_HOT_THRESHOLD",  70))
    LEAD_WARM_THRESHOLD = int(os.environ.get("LEAD_WARM_THRESHOLD", 40))
 
 
class DevelopmentConfig(Config):
    DEBUG   = True
    TESTING = False
 
 
class ProductionConfig(Config):
    """In production always supply SECRET_KEY and DATABASE_URL via env vars."""
    DEBUG   = False
    TESTING = False
 
 
class TestingConfig(Config):
    """Pytest uses an in-memory SQLite DB — fast and disposable."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
 
 
# Map env name → config class (used in run.py and app factory)
config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
 
 
# raise an error in production instead of using a weak default

_raw_password = os.environ.get("ADMIN_PASSWORD", "")
if not _raw_password:
    if os.environ.get("FLASK_ENV") == "production":
        sys.exit("❌ ADMIN_PASSWORD must be set in production!")
    _raw_password = "admin123-dev-only"
ADMIN_PASSWORD = _raw_password 