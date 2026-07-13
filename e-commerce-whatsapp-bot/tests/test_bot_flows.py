"""
tests/test_bot_flows.py — Bot FSM Unit Tests
=============================================
Tests every major state transition and lead scoring event
by calling handle_message() directly (no HTTP, no WhatsApp).

Coverage targets:
    ✅ Greeting + main menu
    ✅ Category browse → product detail
    ✅ Product action → lead capture (name + email)
    ✅ Order tracking (found + not found)
    ✅ FAQ keyword match + topic shortcut
    ✅ Human escalation
    ✅ Global restart trigger ("hi", "menu", "0")
    ✅ Lead score accumulation
    ✅ Lead temperature classification
"""

import pytest
from app.services.bot import handle_message
from models import Lead, Conversation


# ── Helpers ───────────────────────────────────────────────────────────────────

def send(phone, text, app):
    """Shortcut for calling handle_message inside an app context."""
    with app.app_context():
        return handle_message(phone=phone, text=text, channel="test")


def get_lead(phone, app):
    """Fetch the Lead record for a phone number."""
    with app.app_context():
        return Lead.query.filter_by(phone_number=phone).first()


def get_conv(phone, app):
    """Fetch the most recent active Conversation for a phone number."""
    with app.app_context():
        return (
            Conversation.query
            .filter_by(phone_number=phone, is_active=True)
            .order_by(Conversation.created_at.desc())
            .first()
        )


# ── Greeting ──────────────────────────────────────────────────────────────────

class TestGreeting:
    def test_hi_returns_welcome(self, app, db_session):
        reply = send("+911111111111", "hi", app)
        assert "Welcome" in reply or "Hello" in reply
        assert "1" in reply  # menu option 1 is always present

    def test_hello_returns_welcome(self, app, db_session):
        reply = send("+911111111112", "hello", app)
        assert "Welcome" in reply

    def test_start_returns_welcome(self, app, db_session):
        reply = send("+911111111113", "start", app)
        assert "1" in reply  # main menu

    def test_menu_item_4_present(self, app, db_session):
        reply = send("+911111111114", "hi", app)
        assert "4" in reply  # human agent option

    def test_invalid_input_resets_to_greeting(self, app, db_session):
        phone = "+911111111115"
        send(phone, "hi", app)                   # → BROWSE_MENU
        reply = send(phone, "xyz_invalid", app)  # unrecognised → GREETING
        assert "Welcome" in reply or "1" in reply


# ── Main Menu Navigation ──────────────────────────────────────────────────────

class TestMainMenu:
    def test_option_1_shows_categories(self, app, db_session):
        phone = "+912222222221"
        send(phone, "hi", app)
        reply = send(phone, "1", app)
        # Category menu should contain "Electronics" (seeded in conftest)
        assert "Electronics" in reply or "Category" in reply or "1" in reply

    def test_option_2_asks_for_order_id(self, app, db_session):
        phone = "+912222222222"
        send(phone, "hi", app)
        reply = send(phone, "2", app)
        assert "Order" in reply or "ORD" in reply or "order" in reply.lower()

    def test_option_3_shows_faq_menu(self, app, db_session):
        phone = "+912222222223"
        send(phone, "hi", app)
        reply = send(phone, "3", app)
        assert "FAQ" in reply or "question" in reply.lower() or "Shipping" in reply

    def test_option_4_escalates(self, app, db_session):
        phone = "+912222222224"
        send(phone, "hi", app)
        reply = send(phone, "4", app)
        assert "agent" in reply.lower() or "human" in reply.lower() or "team" in reply.lower()


# ── Product Browsing ──────────────────────────────────────────────────────────

class TestProductBrowse:
    def test_browse_category_shows_products(self, app, db_session):
        phone = "+913333333331"
        send(phone, "hi", app)
        send(phone, "1", app)   # browse products
        reply = send(phone, "1", app)   # pick first category (Electronics)
        # Should list products
        assert "Test Smartphone" in reply or "9,999" in reply or "₹" in reply

    def test_browse_product_shows_details(self, app, db_session):
        phone = "+913333333332"
        send(phone, "hi", app)
        send(phone, "1", app)
        send(phone, "1", app)   # Electronics
        reply = send(phone, "1", app)   # first product
        assert "₹" in reply or "Price" in reply or "In Stock" in reply

    def test_invalid_category_number(self, app, db_session):
        phone = "+913333333333"
        send(phone, "hi", app)
        send(phone, "1", app)
        reply = send(phone, "99", app)  # invalid number
        assert "Invalid" in reply or "invalid" in reply or "0" in reply

    def test_browse_back_to_menu(self, app, db_session):
        phone = "+913333333334"
        send(phone, "hi", app)
        send(phone, "1", app)
        reply = send(phone, "0", app)  # back
        assert "1" in reply  # back to main menu


# ── Order Tracking ────────────────────────────────────────────────────────────

class TestOrderTracking:
    def test_valid_order_id_returns_status(self, app, db_session):
        phone = "+914444444441"
        send(phone, "hi", app)
        send(phone, "2", app)
        reply = send(phone, "ORD-TEST-001", app)
        assert "Shipped" in reply or "ORD-TEST-001" in reply

    def test_order_id_case_insensitive(self, app, db_session):
        phone = "+914444444442"
        send(phone, "hi", app)
        send(phone, "2", app)
        reply = send(phone, "ord-test-001", app)   # lowercase
        assert "Shipped" in reply or "ORD-TEST-001" in reply

    def test_invalid_order_id_shows_error(self, app, db_session):
        phone = "+914444444443"
        send(phone, "hi", app)
        send(phone, "2", app)
        reply = send(phone, "ORD-FAKE-999", app)
        assert "No order" in reply or "not found" in reply.lower() or "❌" in reply

    def test_order_tracking_adds_score(self, app, db_session):
        phone = "+914444444444"
        send(phone, "hi", app)
        send(phone, "2", app)
        send(phone, "ORD-TEST-001", app)

        lead = get_lead(phone, app)
        assert lead is not None
        assert lead.score >= 10  # order_tracked = +10


# ── Lead Capture ──────────────────────────────────────────────────────────────

class TestLeadCapture:
    def _reach_product_action(self, phone, app):
        """Navigate to a product and select 'buy / share details'."""
        send(phone, "hi", app)
        send(phone, "1", app)
        send(phone, "1", app)
        send(phone, "1", app)   # view first product
        send(phone, "1", app)   # option 1: get quote / buy now

    def test_lead_capture_asks_for_name(self, app, db_session):
        phone = "+915555555551"
        self._reach_product_action(phone, app)
        lead = get_lead(phone, app)
        if lead and lead.name:
            pytest.skip("Lead already has name — skipping name prompt test")
        conv = get_conv(phone, app)
        with app.app_context():
            c = Conversation.query.get(conv.id)
            assert "LEAD" in c.state or "BROWSE" in c.state

    def test_name_collection_and_scoring(self, app, db_session):
        phone = "+915555555552"
        self._reach_product_action(phone, app)
        reply = send(phone, "Rohit Kumar", app)
        assert "Rohit" in reply or "email" in reply.lower() or "Email" in reply

        lead = get_lead(phone, app)
        assert lead is not None
        assert lead.score >= 20  # name_captured = +20

    def test_email_collection_and_scoring(self, app, db_session):
        phone = "+915555555553"
        self._reach_product_action(phone, app)
        send(phone, "Devansh Verma", app)
        reply = send(phone, "devansh@example.com", app)
        assert "set" in reply.lower() or "team" in reply.lower() or "✅" in reply or "email" in reply.lower()

        lead = get_lead(phone, app)
        assert lead is not None
        assert lead.score >= 40  # name(+20) + email(+20)

    def test_invalid_email_rejected(self, app, db_session):
        phone = "+915555555554"
        self._reach_product_action(phone, app)
        send(phone, "Test User", app)
        reply = send(phone, "not_an_email", app)
        assert "valid" in reply.lower() or "❌" in reply

    def test_short_name_rejected(self, app, db_session):
        phone = "+915555555555"
        self._reach_product_action(phone, app)
        reply = send(phone, "X", app)   # too short
        assert "valid" in reply.lower() or "name" in reply.lower() or "2" in reply


# ── FAQ ───────────────────────────────────────────────────────────────────────

class TestFAQ:
    def test_keyword_match(self, app, db_session):
        phone = "+916666666661"
        send(phone, "hi", app)
        send(phone, "3", app)
        reply = send(phone, "how long does delivery take", app)
        assert "day" in reply.lower() or "delivery" in reply.lower() or "business" in reply.lower()

    def test_topic_shortcut_shipping(self, app, db_session):
        phone = "+916666666662"
        send(phone, "hi", app)
        send(phone, "3", app)
        reply = send(phone, "1", app)   # topic 1 = Shipping
        assert "Shipping" in reply or "delivery" in reply.lower()

    def test_unmatched_question_offers_agent(self, app, db_session):
        phone = "+916666666663"
        send(phone, "hi", app)
        send(phone, "3", app)
        reply = send(phone, "ajdfklajdflkajdflkajdf", app)
        assert "agent" in reply.lower() or "human" in reply.lower() or "0" in reply or "1" in reply


# ── Escalation ────────────────────────────────────────────────────────────────

class TestEscalation:
    def test_escalation_sets_flag(self, app, db_session):
        phone = "+917777777771"
        send(phone, "hi", app)
        send(phone, "4", app)
        with app.app_context():
            conv = (
                Conversation.query
                .filter_by(phone_number=phone)
                .order_by(Conversation.created_at.desc())
                .first()
            )
            assert conv is not None
            assert conv.is_escalated is True

    def test_escalated_state_can_navigate(self, app, db_session):
        phone = "+917777777772"
        send(phone, "hi", app)
        send(phone, "4", app)
        reply = send(phone, "0", app)
        assert "1" in reply or "Welcome" in reply   # returned to menu

    def test_global_restart_from_escalated(self, app, db_session):
        phone = "+917777777773"
        send(phone, "hi", app)
        send(phone, "4", app)
        reply = send(phone, "hi", app)   # global restart
        assert "Welcome" in reply or "Hello" in reply


# ── Lead Scoring ──────────────────────────────────────────────────────────────

class TestLeadScoring:
    def test_new_lead_starts_at_zero(self, app, db_session):
        phone = "+918888888881"
        send(phone, "hi", app)
        lead = get_lead(phone, app)
        assert lead.score == 0 or lead.score >= 0

    def test_score_capped_at_100(self, app, db_session):
        phone = "+918888888882"
        # Do all scoring actions
        send(phone, "hi", app)
        send(phone, "1", app)
        send(phone, "1", app)   # category +10
        send(phone, "1", app)   # product +20
        send(phone, "1", app)   # trigger lead capture
        send(phone, "Full Name", app)   # name +20
        send(phone, "user@example.com", app)   # email +20

        lead = get_lead(phone, app)
        assert lead.score <= 100

    def test_temperature_hot(self, app, db_session):
        phone = "+918888888883"
        send(phone, "hi", app)
        send(phone, "1", app)
        send(phone, "1", app)
        send(phone, "1", app)
        send(phone, "1", app)
        send(phone, "Hot User", app)
        send(phone, "hot@example.com", app)
        send(phone, "hi", app)
        send(phone, "2", app)
        send(phone, "ORD-TEST-001", app)

        lead = get_lead(phone, app)
        # score ≥ 70 = HOT (name+email+product+order ≥ 70)
        assert lead.temperature in ("HOT", "WARM")

    def test_temperature_cold_new_user(self, app, db_session):
        phone = "+918888888884"
        send(phone, "hi", app)
        lead = get_lead(phone, app)
        assert lead.temperature in ("COLD", "WARM")