"""
tests/conftest.py — Shared Pytest Fixtures
===========================================
Provides reusable fixtures for all test modules.

Key fixtures:
    app        → Flask app configured for testing (in-memory SQLite)
    client     → Flask test client (makes HTTP requests in tests)
    db_session → SQLAlchemy session with tables created + seeded
    phone      → A reusable test phone number string

Usage in a test:
    def test_something(client, db_session):
        resp = client.post("/webhook/twilio", data={...})
        assert resp.status_code == 200
"""

import pytest
from app    import create_app
from extensions import db as _db
import models  # noqa: F401 — registers all ORM classes


# ── App fixture ───────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application configured for testing.

    scope="session" means the app is created ONCE for the whole test run,
    which is much faster than creating it per-test.
    The in-memory SQLite DB is wiped automatically when the session ends.
    """
    flask_app = create_app("testing")
    flask_app.config.update({
        "TESTING":               True,
        "WTF_CSRF_ENABLED":      False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TWILIO_ACCOUNT_SID":    "ACtest",
        "TWILIO_AUTH_TOKEN":     "test_token",
        "TWILIO_WHATSAPP_FROM":  "whatsapp:+14155238886",
        "META_ACCESS_TOKEN":     "test_meta_token",
        "META_PHONE_NUMBER_ID":  "123456789",
        "META_VERIFY_TOKEN":     "test_verify",
        "SECRET_KEY":            "test-secret",
        "STORE_NAME":            "Test Store",
        "BOT_NAME":              "TestBot",
        "ADMIN_USERNAME":        "testadmin",
        "ADMIN_PASSWORD":        "testpass",
    })

    yield flask_app


# ── Database fixture ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def db_session(app):
    """
    Create all tables once per session and seed minimal test data.
    Drops all tables after the session ends.
    """
    with app.app_context():
        _db.create_all()
        _seed_test_data()
        yield _db
        _db.drop_all()


def _seed_test_data():
    """Insert minimal data needed for bot flow tests."""
    from models import AdminUser, Category, Product, Order, FAQ

    # Admin user
    if not AdminUser.query.filter_by(username="testadmin").first():
        u = AdminUser(username="testadmin")
        u.set_password("testpass")
        _db.session.add(u)

    # Category
    if not Category.query.filter_by(name="Electronics").first():
        cat = Category(name="Electronics", emoji="📱", is_active=True)
        _db.session.add(cat)
        _db.session.flush()

        # Products
        _db.session.add(Product(
            sku="TEST-001", name="Test Smartphone", price=9999.0,
            category_id=cat.id, in_stock=True, is_featured=True,
            description="A great test phone.",
        ))
        _db.session.add(Product(
            sku="TEST-002", name="Test Laptop", price=49999.0,
            category_id=cat.id, in_stock=False,
            description="An out-of-stock laptop.",
        ))

    # Order
    if not Order.query.filter_by(order_id="ORD-TEST-001").first():
        _db.session.add(Order(
            order_id="ORD-TEST-001",
            customer_name="Test User",
            customer_phone="+919999999999",
            product_name="Test Smartphone",
            status="Shipped",
            amount=9999.0,
            estimated_delivery="25 Jun 2026",
        ))

    # FAQ
    if not FAQ.query.filter_by(question="How long does delivery take?").first():
        _db.session.add(FAQ(
            question="How long does delivery take?",
            answer="Standard delivery takes 3-7 business days.",
            category="Shipping",
            keywords="delivery,shipping,days,time,arrive",
            priority=10,
        ))

    _db.session.commit()


# ── HTTP client fixture ───────────────────────────────────────────────────────

@pytest.fixture
def client(app, db_session):
    """
    Flask test client.
    db_session is included to ensure tables exist before any request.
    """
    with app.test_client() as c:
        with app.app_context():
            yield c


# ── Utility fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def phone():
    """A test phone number to use across test functions."""
    return "+919876543210"


@pytest.fixture
def admin_client(client, app):
    """A test client that is already logged in as admin."""
    with app.app_context():
        from models import AdminUser
        user = AdminUser.query.filter_by(username="testadmin").first()
        if not user:
            user = AdminUser(username="testadmin")
            user.set_password("testpass")
            _db.session.add(user)
            _db.session.commit()

    client.post("/admin/login", data={
        "username": "testadmin",
        "password": "testpass",
    }, follow_redirects=True)
    return client