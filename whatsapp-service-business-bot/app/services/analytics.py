from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func

from ..models import Booking, Conversation, Customer, Lead, Message, Order


def dashboard_metrics() -> dict:
    now = datetime.utcnow()
    since_7 = now - timedelta(days=7)
    revenue = Order.query.filter(Order.status != "cancelled").with_entities(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or Decimal("0")
    orders = Order.query.count()
    conversations = Conversation.query.count()
    leads = Lead.query.count()
    customers = Customer.query.count()
    messages = Message.query.count()
    bookings = Booking.query.count()
    recent_conversations = Conversation.query.filter(Conversation.created_at >= since_7).count()
    completed_orders = Order.query.filter_by(status="completed").count()
    conversion_rate = round((orders / conversations * 100), 1) if conversations else 0
    completion_rate = round((completed_orders / orders * 100), 1) if orders else 0
    return {
        "revenue": float(revenue),
        "orders": orders,
        "conversations": conversations,
        "leads": leads,
        "customers": customers,
        "messages": messages,
        "bookings": bookings,
        "recent_conversations": recent_conversations,
        "conversion_rate": conversion_rate,
        "completion_rate": completion_rate,
    }


def orders_by_status() -> list[tuple[str, int]]:
    return Order.query.with_entities(Order.status, func.count(Order.id)).group_by(Order.status).order_by(func.count(Order.id).desc()).all()


def leads_by_status() -> list[tuple[str, int]]:
    return Lead.query.with_entities(Lead.status, func.count(Lead.id)).group_by(Lead.status).order_by(func.count(Lead.id).desc()).all()


def daily_message_counts(days: int = 7) -> list[dict]:
    start = (datetime.utcnow() - timedelta(days=days - 1)).date()
    rows = (
        Message.query.with_entities(func.date(Message.created_at), func.count(Message.id))
        .filter(func.date(Message.created_at) >= start)
        .group_by(func.date(Message.created_at))
        .all()
    )
    lookup = {str(day): count for day, count in rows}
    series = []
    for i in range(days):
        day = start + timedelta(days=i)
        series.append({"date": day.isoformat(), "count": lookup.get(day.isoformat(), 0)})
    return series
