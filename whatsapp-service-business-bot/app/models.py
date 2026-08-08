from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), default="admin", nullable=False)
    is_active_flag = db.Column(db.Boolean, default=True, nullable=False)

    @property
    def is_active(self) -> bool:  # Flask-Login expects this property.
        return bool(self.is_active_flag)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Customer(TimestampMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=True)
    channel = db.Column(db.String(30), default="whatsapp", nullable=False)
    tags = db.Column(db.String(255), default="")
    notes = db.Column(db.Text, default="")
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    conversations = db.relationship("Conversation", backref="customer", lazy=True)
    orders = db.relationship("Order", backref="customer", lazy=True)
    bookings = db.relationship("Booking", backref="customer", lazy=True)
    leads = db.relationship("Lead", backref="customer", lazy=True)


class Conversation(TimestampMixin, db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    channel = db.Column(db.String(30), default="whatsapp", nullable=False)
    status = db.Column(db.String(30), default="open", nullable=False, index=True)
    state_json = db.Column(db.Text, default="{}", nullable=False)

    messages = db.relationship("Message", backref="conversation", lazy=True, cascade="all, delete-orphan")

    @property
    def state(self) -> dict[str, Any]:
        try:
            return json.loads(self.state_json or "{}")
        except json.JSONDecodeError:
            return {}

    def set_state(self, state: dict[str, Any]) -> None:
        self.state_json = json.dumps(state, ensure_ascii=False)

    def clear_state(self) -> None:
        self.set_state({})


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False, index=True)
    direction = db.Column(db.String(20), nullable=False)  # inbound, outbound, system
    text = db.Column(db.Text, nullable=False)
    external_id = db.Column(db.String(120), nullable=True, index=True)
    meta_json = db.Column(db.Text, default="{}", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @property
    def meta(self) -> dict[str, Any]:
        try:
            return json.loads(self.meta_json or "{}")
        except json.JSONDecodeError:
            return {}

    def set_meta(self, data: dict[str, Any]) -> None:
        self.meta_json = json.dumps(data, ensure_ascii=False)


class MenuItem(TimestampMixin, db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(30), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    description = db.Column(db.Text, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    prep_time_minutes = db.Column(db.Integer, default=15, nullable=False)
    tags = db.Column(db.String(255), default="")

    @property
    def price_float(self) -> float:
        return float(self.price or Decimal("0"))


class FAQ(TimestampMixin, db.Model):
    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False, unique=True)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), default="general", nullable=False)
    keywords = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Order(TimestampMixin, db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=True, index=True)
    status = db.Column(db.String(40), default="confirmed", nullable=False, index=True)
    fulfillment_type = db.Column(db.String(40), default="delivery", nullable=False)
    delivery_address = db.Column(db.Text, default="")
    payment_method = db.Column(db.String(60), default="cash", nullable=False)
    payment_status = db.Column(db.String(40), default="pending", nullable=False)
    notes = db.Column(db.Text, default="")
    subtotal_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    delivery_fee = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def recalculate_totals(self, tax_rate: Decimal = Decimal("0.05"), delivery_fee: Decimal = Decimal("30.00")) -> None:
        subtotal = sum((item.line_total for item in self.items), Decimal("0"))
        self.subtotal_amount = subtotal
        self.tax_amount = (subtotal * tax_rate).quantize(Decimal("0.01"))
        self.delivery_fee = delivery_fee if self.fulfillment_type == "delivery" else Decimal("0.00")
        self.total_amount = (self.subtotal_amount + self.tax_amount + self.delivery_fee).quantize(Decimal("0.01"))


class OrderItem(TimestampMixin, db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    menu_item = db.relationship("MenuItem")


class Booking(TimestampMixin, db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=True, index=True)
    name = db.Column(db.String(160), nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    service_type = db.Column(db.String(100), default="table reservation", nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    party_size = db.Column(db.Integer, default=2, nullable=False)
    status = db.Column(db.String(40), default="confirmed", nullable=False, index=True)
    notes = db.Column(db.Text, default="")


class Lead(TimestampMixin, db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    name = db.Column(db.String(160), nullable=True)
    phone = db.Column(db.String(80), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(60), default="whatsapp", nullable=False)
    interest = db.Column(db.String(255), default="")
    status = db.Column(db.String(40), default="new", nullable=False, index=True)
    notes = db.Column(db.Text, default="")


class Feedback(TimestampMixin, db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=True, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")


class BusinessSetting(TimestampMixin, db.Model):
    __tablename__ = "business_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, default="")


def today_order_count() -> int:
    today = datetime.utcnow().date()
    return Order.query.filter(func.date(Order.created_at) == today).count()
