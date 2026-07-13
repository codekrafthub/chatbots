"""
tests/ — Pytest test suite for the E-Commerce WhatsApp Bot.

Structure:
    conftest.py         — Shared fixtures (app, client, db)
    test_bot_flows.py   — Unit tests for the FSM bot engine
    test_webhooks.py    — Integration tests for webhook endpoints

Run all tests:
    pytest

Run with coverage:
    pytest --cov=app --cov=models --cov-report=term-missing
"""