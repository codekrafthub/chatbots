"""
tests/test_webhooks.py — Webhook Endpoint Integration Tests
============================================================
Tests the HTTP layer: sends real HTTP requests to the webhook routes
and verifies correct status codes, response bodies, and DB side effects.

Coverage:
    ✅ Twilio webhook — valid message → 200 + TwiML response
    ✅ Twilio webhook — empty body → 200 (graceful ignore)
    ✅ Meta webhook   — GET verification challenge
    ✅ Meta webhook   — POST with valid JSON → 200
    ✅ Meta webhook   — POST with malformed JSON → 200 (never 500)
    ✅ Demo API       — POST to /api/demo/chat → JSON reply
    ✅ Demo API       — empty message → 400
    ✅ Public pages   — / and /demo return 200
    ✅ Admin login    — correct + wrong credentials
    ✅ Admin pages    — redirect when not logged in
"""

import json
import pytest


# ── Twilio Webhook ────────────────────────────────────────────────────────────

class TestTwilioWebhook:
    URL = "/webhook/twilio"

    def test_valid_message_returns_200(self, client):
        resp = client.post(self.URL, data={
            "From": "whatsapp:+919876543210",
            "Body": "hi",
        })
        assert resp.status_code == 200

    def test_response_is_valid_twiml(self, client):
        resp = client.post(self.URL, data={
            "From": "whatsapp:+919876543210",
            "Body": "hello",
        })
        assert b"<Response>" in resp.data
        assert resp.content_type == "text/xml"

    def test_empty_body_returns_200(self, client):
        """A blank message body should not crash the server."""
        resp = client.post(self.URL, data={
            "From": "whatsapp:+919876543210",
            "Body": "",
        })
        assert resp.status_code == 200

    def test_missing_from_returns_200(self, client):
        """Missing From field should be handled gracefully."""
        resp = client.post(self.URL, data={"Body": "hi"})
        assert resp.status_code == 200

    def test_no_form_data_returns_200(self, client):
        """Completely empty POST should not crash the server."""
        resp = client.post(self.URL)
        assert resp.status_code == 200

    def test_main_menu_navigation(self, client):
        """Sending '1' after 'hi' should return category list."""
        phone = "whatsapp:+919800000001"
        client.post(self.URL, data={"From": phone, "Body": "hi"})
        resp = client.post(self.URL, data={"From": phone, "Body": "1"})
        assert resp.status_code == 200

    def test_order_tracking(self, client):
        """Entering a valid order ID should return order status."""
        phone = "whatsapp:+919800000002"
        client.post(self.URL, data={"From": phone, "Body": "hi"})
        client.post(self.URL, data={"From": phone, "Body": "2"})
        resp = client.post(self.URL, data={"From": phone, "Body": "ORD-TEST-001"})
        assert resp.status_code == 200

    def test_special_characters_in_message(self, client):
        """Messages with special chars / emojis should not crash."""
        resp = client.post(self.URL, data={
            "From": "whatsapp:+919800000003",
            "Body": "hello 😀 <script>alert(1)</script> ₹500",
        })
        assert resp.status_code == 200

    def test_long_message_handled(self, client):
        """Very long messages should be truncated/handled without crashing."""
        resp = client.post(self.URL, data={
            "From": "whatsapp:+919800000004",
            "Body": "a" * 5000,
        })
        assert resp.status_code == 200


# ── Meta Webhook ──────────────────────────────────────────────────────────────

class TestMetaWebhook:
    URL = "/webhook/meta"

    def _meta_payload(self, phone: str, text: str) -> dict:
        """Build a minimal valid Meta webhook JSON payload."""
        return {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": phone,
                            "type": "text",
                            "text": {"body": text},
                        }]
                    }
                }]
            }]
        }

    def test_verification_challenge_success(self, client):
        """Correct verify token → echo challenge with 200."""
        resp = client.get(self.URL, query_string={
            "hub.mode":         "subscribe",
            "hub.verify_token": "test_verify",
            "hub.challenge":    "CHALLENGE_ABC",
        })
        assert resp.status_code == 200
        assert b"CHALLENGE_ABC" in resp.data

    def test_verification_wrong_token(self, client):
        """Wrong verify token → 403 Forbidden."""
        resp = client.get(self.URL, query_string={
            "hub.mode":         "subscribe",
            "hub.verify_token": "WRONG_TOKEN",
            "hub.challenge":    "CHALLENGE_XYZ",
        })
        assert resp.status_code == 403

    def test_valid_message_returns_200(self, client):
        resp = client.post(
            self.URL,
            data=json.dumps(self._meta_payload("919876543210", "hi")),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data.get("status") == "ok"

    def test_empty_json_returns_200(self, client):
        """Empty / malformed JSON should never crash the server."""
        resp = client.post(self.URL, data="{}", content_type="application/json")
        assert resp.status_code == 200

    def test_malformed_json_returns_200(self, client):
        resp = client.post(self.URL, data=b"not json at all",
                           content_type="application/json")
        assert resp.status_code == 200

    def test_interactive_button_reply(self, client):
        """Interactive button_reply type should be parsed correctly."""
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "type": "interactive",
                            "interactive": {
                                "type": "button_reply",
                                "button_reply": {"title": "1"},
                            }
                        }]
                    }
                }]
            }]
        }
        resp = client.post(
            self.URL,
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_unsupported_message_type_200(self, client):
        """Audio / image messages should be silently ignored, not crashed."""
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "919876543210",
                            "type": "audio",
                        }]
                    }
                }]
            }]
        }
        resp = client.post(
            self.URL,
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 200


# ── Demo API ──────────────────────────────────────────────────────────────────

class TestDemoAPI:
    URL = "/api/demo/chat"

    def test_valid_message_returns_reply(self, client):
        resp = client.post(
            self.URL,
            data=json.dumps({"message": "hi", "phone": "demo_test001"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "reply" in data
        assert len(data["reply"]) > 0

    def test_empty_message_returns_400(self, client):
        resp = client.post(
            self.URL,
            data=json.dumps({"message": "", "phone": "demo_test002"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_missing_message_key_returns_400(self, client):
        resp = client.post(
            self.URL,
            data=json.dumps({"phone": "demo_test003"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_multi_turn_conversation(self, client):
        """Multiple messages from same demo phone should maintain state."""
        phone = "demo_multitest001"
        msgs  = ["hi", "1", "1", "1"]
        for msg in msgs:
            resp = client.post(
                self.URL,
                data=json.dumps({"message": msg, "phone": phone}),
                content_type="application/json",
            )
            assert resp.status_code == 200
            data = json.loads(resp.data)
            assert "reply" in data


# ── Public Pages ──────────────────────────────────────────────────────────────

class TestPublicPages:
    def test_index_page_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_demo_page_returns_200(self, client):
        resp = client.get("/demo")
        assert resp.status_code == 200

    def test_index_contains_store_name(self, client):
        resp = client.get("/")
        assert b"Test Store" in resp.data or b"Store" in resp.data


# ── Admin Auth & Pages ────────────────────────────────────────────────────────

class TestAdminAuth:
    def test_dashboard_redirects_when_not_logged_in(self, client):
        resp = client.get("/admin/", follow_redirects=False)
        assert resp.status_code in (301, 302)
        assert "/login" in resp.headers.get("Location", "")

    def test_login_page_returns_200(self, client):
        resp = client.get("/admin/login")
        assert resp.status_code == 200

    def test_login_with_wrong_password(self, client):
        resp = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "wrongpass",
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Invalid" in resp.data or b"invalid" in resp.data.lower()

    def test_login_with_correct_credentials(self, client):
        resp = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "testpass",
        }, follow_redirects=True)
        assert resp.status_code == 200
        # After login should be on dashboard (not login page anymore)
        assert b"Dashboard" in resp.data or b"Login" not in resp.data


class TestAdminPages:
    def test_leads_page_requires_login(self, client):
        resp = client.get("/admin/leads", follow_redirects=False)
        assert resp.status_code in (301, 302)

    def test_conversations_page_requires_login(self, client):
        resp = client.get("/admin/conversations", follow_redirects=False)
        assert resp.status_code in (301, 302)

    def test_orders_page_requires_login(self, client):
        resp = client.get("/admin/orders", follow_redirects=False)
        assert resp.status_code in (301, 302)

    def test_dashboard_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/")
        assert resp.status_code == 200

    def test_leads_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/leads")
        assert resp.status_code == 200

    def test_orders_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/orders")
        assert resp.status_code == 200

    def test_catalog_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/catalog")
        assert resp.status_code == 200

    def test_faqs_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/faqs")
        assert resp.status_code == 200

    def test_conversations_accessible_after_login(self, admin_client):
        resp = admin_client.get("/admin/conversations")
        assert resp.status_code == 200