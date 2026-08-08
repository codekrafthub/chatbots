from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable

from ..extensions import db
from ..models import MenuItem, Order, OrderItem


ORDER_RE = re.compile(r"\bORD-[A-Z0-9]{6}\b", re.IGNORECASE)
BOOKING_RE = re.compile(r"\bBK-[A-Z0-9]{6}\b", re.IGNORECASE)


def generate_order_number() -> str:
    return f"ORD-{uuid.uuid4().hex[:6].upper()}"


def generate_booking_number() -> str:
    return f"BK-{uuid.uuid4().hex[:6].upper()}"


def money(amount: Decimal | float | int, currency: str = "₹") -> str:
    value = Decimal(str(amount)).quantize(Decimal("0.01"))
    if currency.upper() == "INR" or currency == "₹":
        return f"₹{value}"
    return f"{currency} {value}"


def extract_order_number(text: str) -> str | None:
    match = ORDER_RE.search(text or "")
    return match.group(0).upper() if match else None


def extract_booking_number(text: str) -> str | None:
    match = BOOKING_RE.search(text or "")
    return match.group(0).upper() if match else None


def create_order_from_cart(customer_id: int, conversation_id: int, cart: list[dict], address: str, payment_method: str) -> Order:
    order = Order(
        order_number=generate_order_number(),
        customer_id=customer_id,
        conversation_id=conversation_id,
        status="confirmed",
        fulfillment_type="delivery",
        delivery_address=address,
        payment_method=payment_method,
        payment_status="pending" if payment_method.lower() in {"cash", "cod"} else "awaiting_verification",
    )
    db.session.add(order)
    db.session.flush()

    ids = [int(line["menu_item_id"]) for line in cart]
    items_by_id = {item.id: item for item in MenuItem.query.filter(MenuItem.id.in_(ids)).all()}
    for line in cart:
        item = items_by_id[int(line["menu_item_id"])]
        qty = int(line.get("quantity", 1))
        order.items.append(
            OrderItem(
                menu_item=item,
                quantity=qty,
                unit_price=item.price,
                line_total=item.price * qty,
            )
        )
    order.recalculate_totals()
    return order


def order_status_sentence(order: Order) -> str:
    status_map = {
        "confirmed": "confirmed and sent to the kitchen",
        "preparing": "being prepared",
        "ready": "ready for pickup / dispatch",
        "out_for_delivery": "out for delivery",
        "completed": "completed",
        "cancelled": "cancelled",
    }
    return status_map.get(order.status, order.status.replace("_", " "))


def parse_datetime_human(text: str) -> datetime | None:
    """Small dependency-free parser for student/demo use.

    Supports:
    - 2026-06-05 19:30
    - 05/06/2026 7:30 pm
    - tomorrow 7pm
    - today 20:00
    """
    text = (text or "").strip().lower()
    if not text:
        return None

    patterns = [
        (r"(\d{4}-\d{2}-\d{2})[ t]+(\d{1,2}:\d{2})(?:\s*(am|pm))?", "%Y-%m-%d"),
        (r"(\d{1,2}/\d{1,2}/\d{4})[ t]+(\d{1,2}:\d{2})(?:\s*(am|pm))?", "%d/%m/%Y"),
    ]
    for pattern, date_fmt in patterns:
        match = re.search(pattern, text)
        if match:
            date_part, time_part, meridiem = match.groups()
            try:
                base_date = datetime.strptime(date_part, date_fmt).date()
                hour, minute = [int(x) for x in time_part.split(":")]
                if meridiem == "pm" and hour < 12:
                    hour += 12
                if meridiem == "am" and hour == 12:
                    hour = 0
                return datetime.combine(base_date, datetime.min.time()).replace(hour=hour, minute=minute)
            except ValueError:
                return None

    rel_match = re.search(r"\b(today|tomorrow)\b.*?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if rel_match:
        day_word, hour_s, minute_s, meridiem = rel_match.groups()
        base = datetime.now().replace(second=0, microsecond=0)
        if day_word == "tomorrow":
            base += timedelta(days=1)
        hour = int(hour_s)
        minute = int(minute_s or 0)
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        try:
            return base.replace(hour=hour, minute=minute)
        except ValueError:
            return None
    return None


def merge_cart(existing: list[dict], new_lines: Iterable[dict]) -> list[dict]:
    merged: dict[int, int] = {}
    for line in existing:
        merged[int(line["menu_item_id"])] = merged.get(int(line["menu_item_id"]), 0) + int(line.get("quantity", 1))
    for line in new_lines:
        merged[int(line["menu_item_id"])] = merged.get(int(line["menu_item_id"]), 0) + int(line.get("quantity", 1))
    return [{"menu_item_id": item_id, "quantity": qty} for item_id, qty in merged.items() if qty > 0]
