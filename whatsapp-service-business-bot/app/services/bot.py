from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal

from flask import current_app

from ..extensions import db
from ..models import Booking, Conversation, Customer, Feedback, Lead, Message, Order
from .faq import faq_categories_summary, match_faq
from .menu import cart_summary, find_items_by_query, format_menu, parse_cart_lines
from .orders import (
    create_order_from_cart,
    extract_booking_number,
    extract_order_number,
    generate_booking_number,
    money,
    order_status_sentence,
    parse_datetime_human,
    merge_cart,
)


HELP_TEXT = """👋 I can help you with:
1. `menu` — view menu
2. `order` — place a food order
3. `status ORD-XXXXXX` — track order
4. `book` — reserve a table / appointment
5. `faq` — common questions
6. `human` — request staff callback
7. `feedback` — rate your experience"""


def process_incoming_message(phone: str, text: str, channel: str = "demo", profile_name: str | None = None, external_id: str | None = None, meta: dict | None = None) -> str:
    clean_phone = (phone or "anonymous").strip()
    customer = Customer.query.filter_by(phone=clean_phone).first()
    if not customer:
        customer = Customer(phone=clean_phone, channel=channel, name=profile_name)
        db.session.add(customer)
        db.session.flush()
    elif profile_name and not customer.name:
        customer.name = profile_name
    customer.last_seen_at = datetime.utcnow()

    conversation = (
        Conversation.query.filter_by(customer_id=customer.id, status="open")
        .order_by(Conversation.updated_at.desc())
        .first()
    )
    if not conversation:
        conversation = Conversation(customer_id=customer.id, channel=channel, status="open")
        db.session.add(conversation)
        db.session.flush()

    inbound = Message(conversation_id=conversation.id, direction="inbound", text=text or "", external_id=external_id)
    inbound.set_meta(meta or {})
    db.session.add(inbound)
    db.session.flush()

    engine = BotEngine(customer, conversation)
    reply = engine.handle(text or "")

    outbound = Message(conversation_id=conversation.id, direction="outbound", text=reply)
    db.session.add(outbound)
    db.session.commit()
    return reply


class BotEngine:
    def __init__(self, customer: Customer, conversation: Conversation):
        self.customer = customer
        self.conversation = conversation

    @property
    def state(self) -> dict:
        return self.conversation.state

    def set_state(self, state: dict) -> None:
        self.conversation.set_state(state)

    def clear_state(self) -> None:
        self.conversation.clear_state()

    def handle(self, text: str) -> str:
        text = (text or "").strip()
        lowered = text.lower()

        if not text:
            return "Please send a message. Type `help` to see available options."
        if lowered in {"cancel", "stop", "reset", "restart"}:
            self.clear_state()
            return "No problem. I have reset the current flow. Type `menu`, `order`, `book`, or `help`."

        state = self.state
        flow = state.get("flow")
        if flow == "order":
            return self._handle_order_flow(text)
        if flow == "booking":
            return self._handle_booking_flow(text)
        if flow == "lead":
            return self._handle_lead_flow(text)
        if flow == "feedback":
            return self._handle_feedback_flow(text)

        if any(word in lowered for word in ["hi", "hello", "hey", "start", "namaste"]):
            return self._welcome()
        if "help" in lowered:
            return HELP_TEXT
        if lowered in {"menu", "show menu", "items", "food"} or "menu" in lowered:
            return format_menu()
        if lowered.startswith("order") or "add " in lowered or parse_cart_lines(text):
            self.set_state({"flow": "order", "step": "items", "cart": []})
            return self._handle_order_flow(text.replace("order", "", 1).strip() or "order")
        if "status" in lowered or "track" in lowered or extract_order_number(text):
            return self._handle_status(text)
        if "book" in lowered or "reservation" in lowered or "appointment" in lowered or "table" in lowered:
            self.set_state({"flow": "booking", "step": "name"})
            return "📅 Sure. Please send the booking name. Example: `Rohit Kumar`"
        if "faq" in lowered or "question" in lowered:
            return "❓ " + faq_categories_summary() + "\nAsk naturally, e.g., `Do you deliver?` or `What are your opening hours?`"
        if any(word in lowered for word in ["human", "agent", "staff", "callback", "support", "complaint", "catering", "bulk", "event"]):
            self.set_state({"flow": "lead", "step": "details", "interest": text})
            return "👤 I will ask our staff to contact you. Please send your name and requirement in one message. Example: `Rohit, corporate lunch for 30 people tomorrow`."
        if "feedback" in lowered or "review" in lowered or "rating" in lowered:
            self.set_state({"flow": "feedback", "step": "rating"})
            return "⭐ Please rate your experience from 1 to 5."
        if "hour" in lowered or "open" in lowered or "timing" in lowered:
            return f"🕒 We are open: {current_app.config['BUSINESS_OPENING_HOURS']}"
        if "location" in lowered or "address" in lowered or "where" in lowered:
            return f"📍 Address: {current_app.config['BUSINESS_ADDRESS']}\nPhone: {current_app.config['BUSINESS_PHONE']}"

        faq = match_faq(text)
        if faq:
            return f"❓ {faq.answer}\n\nType `menu`, `order`, `book`, or `human` for more help."

        matches = find_items_by_query(text, limit=3)
        if matches:
            lines = ["I found these menu items:"]
            for item in matches:
                lines.append(f"{item.sku} — {item.name}: {money(item.price, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}")
            lines.append("Reply with SKUs and quantity to order, e.g., `PZ01 x2`.")
            return "\n".join(lines)

        return "I did not fully understand that. " + HELP_TEXT

    def _welcome(self) -> str:
        name = current_app.config["BUSINESS_NAME"]
        return f"Welcome to {name}!\n\n" + HELP_TEXT

    def _handle_order_flow(self, text: str) -> str:
        state = self.state
        step = state.get("step", "items")
        cart = state.get("cart", [])
        lowered = text.lower().strip()

        if step == "items":
            if lowered in {"order", "start order"}:
                return format_menu() + "\n\nSend item SKUs and quantities, e.g., `PZ01 x2, BR01 x1`."
            if lowered in {"cart", "show cart"}:
                summary, _ = cart_summary(cart)
                return summary + "\nSend more items or type `done` to checkout."
            if lowered in {"done", "checkout", "confirm"}:
                if not cart:
                    return "Your cart is empty. Send items like `PZ01 x2` or type `menu`."
                state["step"] = "address"
                self.set_state(state)
                summary, _ = cart_summary(cart)
                return summary + "\n\n📍 Please send delivery address. For pickup, type `pickup`."

            new_lines = parse_cart_lines(text)
            if not new_lines:
                return "I could not identify items. Send SKUs from the menu, e.g., `PZ01 x2, BR01 x1`, or type `menu`."
            cart = merge_cart(cart, new_lines)
            state["cart"] = cart
            self.set_state(state)
            summary, _ = cart_summary(cart)
            return summary + "\n\nSend more items, `cart`, or `done` to checkout."

        if step == "address":
            if lowered == "pickup":
                state["fulfillment_type"] = "pickup"
                state["address"] = "Customer pickup"
            else:
                state["fulfillment_type"] = "delivery"
                state["address"] = text
            state["step"] = "payment"
            self.set_state(state)
            return "💳 Payment method? Reply `cash`, `upi`, or `card`."

        if step == "payment":
            method = lowered if lowered in {"cash", "cod", "upi", "card"} else text[:60]
            order = create_order_from_cart(
                customer_id=self.customer.id,
                conversation_id=self.conversation.id,
                cart=cart,
                address=state.get("address", ""),
                payment_method=method,
            )
            order.fulfillment_type = state.get("fulfillment_type", "delivery")
            order.recalculate_totals(delivery_fee=Decimal("0.00") if order.fulfillment_type == "pickup" else Decimal("30.00"))
            self.clear_state()
            item_lines = [f"- {line.menu_item.name} x {line.quantity}" for line in order.items]
            return (
                f"✅ Order confirmed!\n"
                f"Order No: *{order.order_number}*\n"
                + "\n".join(item_lines)
                + f"\nTotal: {money(order.total_amount, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}\n"
                f"Status: {order_status_sentence(order)}\n"
                "Use `status ORD-XXXXXX` anytime to track it."
            )

        self.clear_state()
        return "The order flow was reset. Type `order` to start again."

    def _handle_status(self, text: str) -> str:
        order_number = extract_order_number(text)
        if order_number:
            order = Order.query.filter_by(order_number=order_number).first()
        else:
            order = Order.query.filter_by(customer_id=self.customer.id).order_by(Order.created_at.desc()).first()
        if not order:
            return "I could not find an order for this number. Send `status ORD-XXXXXX` or place a new order with `order`."
        return (
            f"📦 Order *{order.order_number}* is {order_status_sentence(order)}.\n"
            f"Payment: {order.payment_status}\n"
            f"Total: {money(order.total_amount, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}\n"
            f"Address: {order.delivery_address or 'Pickup'}"
        )

    def _handle_booking_flow(self, text: str) -> str:
        state = self.state
        step = state.get("step", "name")
        if step == "name":
            state["name"] = text.strip()[:160]
            state["step"] = "datetime"
            self.set_state(state)
            return "Great. Send date and time. Example: `2026-06-05 19:30` or `tomorrow 7pm`."
        if step == "datetime":
            scheduled_for = parse_datetime_human(text)
            if not scheduled_for:
                return "I could not read the date/time. Please use `YYYY-MM-DD HH:MM`, e.g., `2026-06-05 19:30`, or `tomorrow 7pm`."
            if scheduled_for < datetime.now():
                return "That time seems to be in the past. Please send a future date/time."
            state["scheduled_for"] = scheduled_for.isoformat()
            state["step"] = "party_size"
            self.set_state(state)
            return "How many people? Example: `4`"
        if step == "party_size":
            match = re.search(r"\d+", text)
            if not match:
                return "Please send the number of people, e.g., `4`."
            party_size = max(1, min(int(match.group()), 50))
            booking = Booking(
                booking_number=generate_booking_number(),
                customer_id=self.customer.id,
                conversation_id=self.conversation.id,
                name=state.get("name", self.customer.name or "Guest"),
                phone=self.customer.phone,
                scheduled_for=datetime.fromisoformat(state["scheduled_for"]),
                party_size=party_size,
                service_type="table reservation",
                status="confirmed",
            )
            db.session.add(booking)
            self.clear_state()
            return (
                f"✅ Booking confirmed!\n"
                f"Booking No: *{booking.booking_number}*\n"
                f"Name: {booking.name}\n"
                f"Time: {booking.scheduled_for.strftime('%d %b %Y, %I:%M %p')}\n"
                f"People: {booking.party_size}\n"
                "Our team will contact you if confirmation is needed."
            )
        self.clear_state()
        return "The booking flow was reset. Type `book` to start again."

    def _handle_lead_flow(self, text: str) -> str:
        state = self.state
        interest = state.get("interest", "Customer requested staff support")
        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)
        name = text.split(",")[0].strip()[:160] if text else self.customer.name
        lead = Lead(
            customer_id=self.customer.id,
            name=name or self.customer.name,
            phone=self.customer.phone,
            email=email_match.group(0) if email_match else None,
            interest=interest[:255],
            notes=text,
            status="new",
            source=self.customer.channel,
        )
        db.session.add(lead)
        self.clear_state()
        return "✅ Thank you. Your request has been shared with our staff. A team member will contact you soon."

    def _handle_feedback_flow(self, text: str) -> str:
        state = self.state
        step = state.get("step", "rating")
        if step == "rating":
            match = re.search(r"[1-5]", text)
            if not match:
                return "Please send a rating from 1 to 5."
            state["rating"] = int(match.group())
            state["step"] = "comment"
            self.set_state(state)
            return "Thanks. Please add a short comment, or type `skip`."
        comment = "" if text.lower().strip() == "skip" else text.strip()
        db.session.add(
            Feedback(
                customer_id=self.customer.id,
                conversation_id=self.conversation.id,
                rating=int(state.get("rating", 5)),
                comment=comment,
            )
        )
        self.clear_state()
        return "🙏 Thank you for your feedback. It helps us improve."
