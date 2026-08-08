from __future__ import annotations

import csv
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from flask import current_app

from ..extensions import db
from ..models import Booking, Conversation, Customer, FAQ, Lead, MenuItem, Message, Order, OrderItem, User
from .orders import generate_booking_number, generate_order_number


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def ensure_default_admin() -> None:
    email = current_app.config["ADMIN_EMAIL"].strip().lower()
    user = User.query.filter_by(email=email).first()
    if user:
        return
    user = User(name=current_app.config["ADMIN_NAME"], email=email, role="admin")
    user.set_password(current_app.config["ADMIN_PASSWORD"])
    db.session.add(user)
    db.session.commit()


def seed_reference_data() -> None:
    seed_menu_items()
    seed_faqs()


def seed_menu_items() -> None:
    path = DATA_DIR / "menu.csv"
    if not path.exists():
        return
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sku = row["sku"].strip().upper()
            item = MenuItem.query.filter_by(sku=sku).first()
            if item:
                continue
            item = MenuItem(
                sku=sku,
                name=row["name"].strip(),
                category=row["category"].strip(),
                description=row.get("description", "").strip(),
                price=Decimal(row["price"].strip()),
                prep_time_minutes=int(row.get("prep_time_minutes") or 15),
                tags=row.get("tags", "").strip(),
                is_available=(row.get("is_available", "true").strip().lower() != "false"),
            )
            db.session.add(item)
    db.session.commit()


def seed_faqs() -> None:
    path = DATA_DIR / "faqs.csv"
    if not path.exists():
        return
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            question = row["question"].strip()
            faq = FAQ.query.filter_by(question=question).first()
            if faq:
                continue
            db.session.add(
                FAQ(
                    question=question,
                    answer=row["answer"].strip(),
                    category=row.get("category", "general").strip() or "general",
                    keywords=row.get("keywords", "").strip(),
                    is_active=(row.get("is_active", "true").strip().lower() != "false"),
                )
            )
    db.session.commit()


def seed_demo_analytics() -> None:
    """Create small demo records once, so the dashboard looks useful immediately."""
    if Customer.query.filter(Customer.phone.like("demo:%")).count() > 0:
        return
    if MenuItem.query.count() == 0:
        seed_menu_items()

    items = MenuItem.query.filter_by(is_available=True).limit(4).all()
    now = datetime.utcnow()
    for idx in range(1, 6):
        customer = Customer(
            phone=f"demo:+91000000000{idx}",
            name=f"Demo Customer {idx}",
            channel="demo",
            last_seen_at=now - timedelta(hours=idx),
        )
        db.session.add(customer)
        db.session.flush()
        conv = Conversation(customer_id=customer.id, channel="demo", status="open")
        db.session.add(conv)
        db.session.flush()
        db.session.add(Message(conversation_id=conv.id, direction="inbound", text="menu"))
        db.session.add(Message(conversation_id=conv.id, direction="outbound", text="Here is our menu."))
        if idx <= 3 and items:
            order = Order(
                order_number=generate_order_number(),
                customer_id=customer.id,
                conversation_id=conv.id,
                status=["confirmed", "preparing", "completed"][idx - 1],
                fulfillment_type="delivery",
                delivery_address=f"Demo Street {idx}, Pune",
                payment_method="cash",
            )
            db.session.add(order)
            db.session.flush()
            selected = items[idx % len(items)]
            order.items.append(
                OrderItem(
                    menu_item_id=selected.id,
                    quantity=idx,
                    unit_price=selected.price,
                    line_total=selected.price * idx,
                )
            )
            order.recalculate_totals()
        if idx == 4:
            db.session.add(
                Booking(
                    booking_number=generate_booking_number(),
                    customer_id=customer.id,
                    conversation_id=conv.id,
                    name=customer.name,
                    phone=customer.phone,
                    scheduled_for=now + timedelta(days=1, hours=2),
                    party_size=4,
                    status="confirmed",
                )
            )
        if idx == 5:
            db.session.add(
                Lead(
                    customer_id=customer.id,
                    name=customer.name,
                    phone=customer.phone,
                    interest="Corporate catering inquiry",
                    status="new",
                    source="demo",
                )
            )
    db.session.commit()
