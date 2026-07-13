"""
app/services/analytics.py — Analytics & Reporting Service
===========================================================
Aggregates database data into the metrics shown on the admin dashboard.

All functions return plain Python dicts/lists so they can be passed
directly to Jinja2 templates or serialised to JSON for chart.js.

Functions
─────────
get_summary_stats()          → top-level KPI cards
get_daily_message_counts()   → message volume by day (line chart)
get_lead_funnel()            → leads per pipeline stage (funnel chart)
get_conversion_rate()        → percentage of leads that converted
get_top_product_interests()  → most-browsed product categories (bar chart)
get_lead_temperature_breakdown() → HOT / WARM / COLD counts (doughnut)
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models import Conversation, Message, Lead, Order

logger = logging.getLogger(__name__)


def get_summary_stats() -> dict:
    """
    Return the six KPI cards shown at the top of the dashboard.

    Returns dict with keys:
        total_leads, total_conversations, total_orders,
        conversion_rate, hot_leads, escalated_today
    """
    today = datetime.utcnow().date()

    total_leads         = Lead.query.count()
    total_conversations = Conversation.query.count()
    total_orders        = Order.query.count()
    hot_leads           = Lead.query.filter(Lead.score >= 70).count()
    escalated_today     = (
        Conversation.query
        .filter(
            Conversation.is_escalated == True,
            func.date(Conversation.updated_at) == today,
        )
        .count()
    )

    return {
        "total_leads":         total_leads,
        "total_conversations": total_conversations,
        "total_orders":        total_orders,
        "conversion_rate":     get_conversion_rate(),
        "hot_leads":           hot_leads,
        "escalated_today":     escalated_today,
    }


def get_daily_message_counts(days: int = 7) -> list:
    """
    Message volume per day for the last `days` days.

    Returns:
        List of {'date': 'YYYY-MM-DD', 'count': N} sorted oldest → newest.
        Missing days are NOT zero-filled (frontend handles that).
    """
    since = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.session.query(
            func.date(Message.created_at).label("date"),
            func.count(Message.id).label("count"),
        )
        .filter(Message.created_at >= since)
        .group_by(func.date(Message.created_at))
        .order_by(func.date(Message.created_at))
        .all()
    )

    return [{"date": str(r.date), "count": r.count} for r in rows]


def get_lead_funnel() -> dict:
    """
    Lead counts at each pipeline stage.

    Returns:
        {'new': N, 'qualified': N, 'interested': N, 'converted': N}
    """
    stages = ("new", "qualified", "interested", "converted")
    return {s: Lead.query.filter_by(stage=s).count() for s in stages}


def get_conversion_rate() -> float:
    """
    Percentage of total leads that reached the 'converted' stage.

    Returns:
        Float like 12.5 (meaning 12.5%). Returns 0.0 if no leads exist.
    """
    total     = Lead.query.count()
    converted = Lead.query.filter_by(stage="converted").count()

    if total == 0:
        return 0.0
    return round((converted / total) * 100, 1)


def get_top_product_interests(limit: int = 5) -> list:
    """
    Most common product_interest values across all leads.

    Returns:
        List of {'interest': str, 'count': int}, ordered by count desc.
    """
    rows = (
        db.session.query(
            Lead.product_interest,
            func.count(Lead.id).label("count"),
        )
        .filter(Lead.product_interest.isnot(None))
        .filter(Lead.product_interest != "")
        .group_by(Lead.product_interest)
        .order_by(func.count(Lead.id).desc())
        .limit(limit)
        .all()
    )

    return [{"interest": r.product_interest, "count": r.count} for r in rows]


def get_lead_temperature_breakdown() -> dict:
    """
    HOT / WARM / COLD counts for the doughnut chart.

    Returns:
        {'HOT': N, 'WARM': N, 'COLD': N}
    """
    all_leads = Lead.query.all()
    return {
        "HOT":  sum(1 for l in all_leads if l.temperature == "HOT"),
        "WARM": sum(1 for l in all_leads if l.temperature == "WARM"),
        "COLD": sum(1 for l in all_leads if l.temperature == "COLD"),
    }


def get_recent_activity(limit: int = 10) -> list:
    """
    Return the most recently updated conversations for a live activity feed.

    Returns:
        List of Conversation objects.
    """
    from models import Conversation
    return (
        Conversation.query
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .all()
    )