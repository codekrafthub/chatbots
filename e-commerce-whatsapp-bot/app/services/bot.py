"""
app/services/bot.py — Core Bot Logic (Finite State Machine)
===========================================================
Every incoming WhatsApp message flows through handle_message() which
dispatches to the right handler based on the conversation's current state.

FSM States
──────────
GREETING         Welcome + main menu display
BROWSE_MENU      Waiting for main menu selection (1-4)
BROWSE_CATEGORY  Waiting for category number
BROWSE_PRODUCT:<cat_id>   Waiting for product number within a category
PRODUCT_ACTION:<prod_id>:<cat_id>  After viewing a product (buy / browse more)
TRACK_ORDER      Waiting for the user to type their Order ID
FAQ              Waiting for a question or topic number
LEAD_NAME        Collecting the user's name
LEAD_EMAIL       Collecting the user's email
ESCALATED        Handed to a human agent

Global triggers (work from ANY state)
──────────────────────────────────────
hi / hello / hey / start / menu / 0 / restart  → restart from GREETING

Lead Scoring Events
───────────────────
name_captured   +20   email_captured  +20
category_viewed +10   product_viewed  +20
order_tracked   +10
"""

import logging
from extensions import db
from models import Conversation, Message, Lead

logger = logging.getLogger(__name__)


# ─── State constants ──────────────────────────────────────────────────────────

class S:
    """String constants for every FSM state."""
    GREETING        = "GREETING"
    BROWSE_MENU     = "BROWSE_MENU"
    BROWSE_CATEGORY = "BROWSE_CATEGORY"
    TRACK_ORDER     = "TRACK_ORDER"
    FAQ             = "FAQ"
    LEAD_NAME       = "LEAD_NAME"
    LEAD_EMAIL      = "LEAD_EMAIL"
    ESCALATED       = "ESCALATED"
    # Dynamic states — use string prefix matching
    BROWSE_PRODUCT  = "BROWSE_PRODUCT"   # stored as "BROWSE_PRODUCT:<cat_id>"
    PRODUCT_ACTION  = "PRODUCT_ACTION"   # stored as "PRODUCT_ACTION:<prod_id>:<cat_id>"


# ─── Public entry point ───────────────────────────────────────────────────────

def handle_message(phone: str, text: str, channel: str) -> str:
    """
    Process one incoming WhatsApp message and return the bot's reply.

    Args:
        phone:   Sender's phone number (E.164 format, e.g. '+919876543210')
        text:    Raw message body from WhatsApp
        channel: 'twilio' | 'meta' | 'demo'

    Returns:
        Reply string to send back to the user.
    """
    text = text.strip()

    # ── Fetch or create DB records ────────────────────────────────────────────
    conv = _get_or_create_conversation(phone, channel)
    lead = _get_or_create_lead(phone)

    # ── Log inbound message ───────────────────────────────────────────────────
    _log_message(conv, direction="in", content=text)

    try:
        reply = _route(conv, lead, text)
        _log_message(conv, direction="out", content=reply)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return reply


# ─── Router ───────────────────────────────────────────────────────────────────

def _route(conv: Conversation, lead: Lead, text: str) -> str:
    """Dispatch to the right handler based on state and global triggers."""

    # Global restart triggers
    if _is_restart(text):
        return _greeting(conv, lead)

    state = conv.state

    # ── Dynamic prefix-matched states ─────────────────────────────────────────
    if state.startswith(S.BROWSE_PRODUCT):
        return _browse_product(conv, lead, text)

    if state.startswith(S.PRODUCT_ACTION):
        return _product_action(conv, lead, text)

    # ── Static state dispatch ─────────────────────────────────────────────────
    dispatch = {
        S.GREETING:        _greeting,
        S.BROWSE_MENU:     _main_menu,
        S.BROWSE_CATEGORY: _browse_category,
        S.TRACK_ORDER:     _track_order,
        S.FAQ:             _faq,
        S.LEAD_NAME:       _collect_name,
        S.LEAD_EMAIL:      _collect_email,
        S.ESCALATED:       _escalated,
    }

    handler = dispatch.get(state, _greeting)
    return handler(conv, lead, text)


# ─── State handlers ───────────────────────────────────────────────────────────

def _greeting(conv: Conversation, lead: Lead, text: str = "") -> str:
    """Welcome message + main menu."""
    conv.state = S.BROWSE_MENU
    name_part  = f"Hi *{lead.name}*! 👋" if lead.name else "Hello! 👋"

    return (
        f"{name_part} Welcome to *{_store_name()}*! 🛍️\n"
        f"I'm {_bot_name()}, your personal shopping assistant.\n\n"
        f"What can I help you with today?\n\n"
        f"1️⃣  Browse Products\n"
        f"2️⃣  Track My Order\n"
        f"3️⃣  FAQs & Help\n"
        f"4️⃣  Talk to a Human Agent\n\n"
        f"↩️  Reply with 1, 2, 3, or 4"
    )


def _main_menu(conv: Conversation, lead: Lead, text: str) -> str:
    """Handle main menu selection (1-4)."""
    if text == "1":
        return _show_categories(conv)

    elif text == "2":
        conv.state = S.TRACK_ORDER
        return (
            "📦 *Order Tracking*\n\n"
            "Please enter your *Order ID* (e.g. ORD-1234):\n\n"
            "↩️  Type *0* to go back"
        )

    elif text == "3":
        conv.state = S.FAQ
        return (
            "❓ *FAQs & Help*\n\n"
            "Type your question, or pick a topic:\n\n"
            "1️⃣  Shipping & Delivery\n"
            "2️⃣  Returns & Refunds\n"
            "3️⃣  Payment Methods\n"
            "4️⃣  Product Availability\n\n"
            "↩️  Type *0* for main menu"
        )

    elif text == "4":
        return _escalate(conv, lead)

    else:
        return _greeting(conv, lead)


# ─── Product Catalogue ────────────────────────────────────────────────────────

def _show_categories(conv: Conversation) -> str:
    """List all active product categories."""
    from app.services.catalog import get_active_categories
    conv.state = S.BROWSE_CATEGORY
    categories = get_active_categories()

    if not categories:
        return "😕 No categories available right now.\n\nType *0* for main menu."

    lines = ["🛍️ *Shop by Category*\n"]
    for i, cat in enumerate(categories, 1):
        lines.append(f"{i}️⃣  {cat.emoji} {cat.name}")
    lines.append("\n↩️  Reply with a number to browse | *0* for main menu")
    return "\n".join(lines)


def _browse_category(conv: Conversation, lead: Lead, text: str) -> str:
    """User has selected a category number — show its products."""
    from app.services.catalog import get_active_categories, get_products_by_category

    if text == "0":
        return _greeting(conv, lead)

    try:
        idx        = int(text) - 1
        categories = get_active_categories()

        if 0 <= idx < len(categories):
            cat      = categories[idx]
            products = get_products_by_category(cat.id)

            # Score the lead for showing category interest
            lead.product_interest = cat.name
            _add_score(lead, "category_viewed")

            if not products:
                return (
                    f"😕 No products in *{cat.name}* right now.\n\n"
                    "Type *0* for main menu."
                )

            lines = [f"{cat.emoji} *{cat.name}*\n"]
            for i, p in enumerate(products, 1):
                stock = "✅" if p.in_stock else "❌"
                lines.append(f"{i}️⃣  {p.name} — ₹{p.price:,.0f} {stock}")
            lines.append("\n↩️  Pick a product number for details | *0* main menu")

            # Encode category ID in the state string for next step
            conv.state = f"{S.BROWSE_PRODUCT}:{cat.id}"
            return "\n".join(lines)

    except (ValueError, IndexError):
        pass

    return "❌ Invalid choice. Please enter the category number.\n↩️  *0* main menu"


def _browse_product(conv: Conversation, lead: Lead, text: str) -> str:
    """User selected a product — show full details."""
    from app.services.catalog import get_products_by_category

    if text == "0":
        return _greeting(conv, lead)
    if text.lower() == "back":
        return _show_categories(conv)

    # Extract category_id from state "BROWSE_PRODUCT:<cat_id>"
    cat_id = None
    parts  = conv.state.split(":")
    if len(parts) == 2:
        try:
            cat_id = int(parts[1])
        except ValueError:
            pass

    try:
        idx      = int(text) - 1
        products = get_products_by_category(cat_id) if cat_id else []

        if 0 <= idx < len(products):
            p = products[idx]

            # Score for specific product interest
            lead.product_interest = f"{p.category.name} > {p.name}" if p.category else p.name
            _add_score(lead, "product_viewed")

            stock_text = "✅ In Stock" if p.in_stock else "❌ Out of Stock"
            lines = [
                f"🛒 *{p.name}*",
                f"",
                f"💰 Price:  ₹{p.price:,.0f}",
                f"📦 Stock:  {stock_text}",
                f"🏷️  SKU:    {p.sku}",
                f"",
                p.description or "Premium quality product.",
                f"",
                f"What would you like to do?",
                f"",
            ]
            if p.in_stock:
                lines += [
                    "1️⃣  Get a Quote / Buy Now",
                    "2️⃣  Browse More Products",
                    "3️⃣  Share my details for exclusive offers",
                    "0️⃣  Main Menu",
                ]
            else:
                lines += [
                    "1️⃣  Notify me when back in stock",
                    "2️⃣  Browse More Products",
                    "0️⃣  Main Menu",
                ]

            # Encode product + category in state
            conv.state = f"{S.PRODUCT_ACTION}:{p.id}:{cat_id or 0}"
            return "\n".join(lines)

    except (ValueError, IndexError):
        pass

    return "❌ Invalid choice. Enter the product number.\n↩️  *0* main menu"


def _product_action(conv: Conversation, lead: Lead, text: str) -> str:
    """Handle user's decision after viewing a product."""
    if text == "0":
        return _greeting(conv, lead)

    if text in ("1", "3"):
        # They want to buy / get notified / share details → lead capture
        return _start_lead_capture(conv, lead)

    if text == "2":
        # Browse more — go back to category listing
        return _show_categories(conv)

    return _greeting(conv, lead)


# ─── Order Tracking ───────────────────────────────────────────────────────────

def _track_order(conv: Conversation, lead: Lead, text: str) -> str:
    """Look up an order by ID and return its current status."""
    from app.services.orders import get_order_status

    if text == "0":
        return _greeting(conv, lead)

    order = get_order_status(text.strip().upper())

    if order:
        _add_score(lead, "order_tracked")
        conv.state = S.BROWSE_MENU

        emoji_map = {
            "Processing":       "⏳",
            "Confirmed":        "✅",
            "Shipped":          "🚚",
            "Out for Delivery": "🏍️",
            "Delivered":        "📦",
            "Cancelled":        "❌",
        }
        status_emoji = emoji_map.get(order.status, "📦")

        reply = (
            f"🔍 *Order Found!*\n\n"
            f"📋 Order ID:   {order.order_id}\n"
            f"🛒 Product:    {order.product_name}\n"
            f"{status_emoji} Status:     {order.status}\n"
        )
        if order.estimated_delivery:
            reply += f"📅 Est. Delivery: {order.estimated_delivery}\n"
        if order.tracking_url:
            reply += f"🔗 Track: {order.tracking_url}\n"

        reply += "\n↩️  Type *0* for main menu or enter another Order ID."
        return reply

    return (
        f"❌ No order found with ID *{text.strip().upper()}*.\n\n"
        f"Double-check your Order ID and try again, or type *0* for main menu."
    )


# ─── FAQ ─────────────────────────────────────────────────────────────────────

def _faq(conv: Conversation, lead: Lead, text: str) -> str:
    """Answer FAQ questions via keyword matching or topic shortcuts."""
    from app.services.faq import find_best_faq, get_faqs_by_category

    if text == "0":
        return _greeting(conv, lead)

    # Topic shortcuts (1-4 map to categories)
    topic_map = {"1": "Shipping", "2": "Returns", "3": "Payment", "4": "Availability"}
    if text in topic_map:
        category = topic_map[text]
        faqs     = get_faqs_by_category(category)

        if faqs:
            lines = [f"📚 *{category} FAQs*\n"]
            for faq in faqs[:3]:
                lines.append(f"❓ {faq.question}")
                lines.append(f"💬 {faq.answer}\n")
            lines.append("Type *0* for main menu or ask another question.")
            return "\n".join(lines)

    # Keyword search for free-text questions
    faq = find_best_faq(text)
    if faq:
        return (
            f"❓ *{faq.question}*\n\n"
            f"💬 {faq.answer}\n\n"
            f"Was this helpful?\n"
            f"Type *0* for main menu or ask another question."
        )

    # No match found
    conv.state = S.BROWSE_MENU
    return (
        "🤔 I couldn't find an exact answer.\n\n"
        "Would you like to:\n"
        "1️⃣  Talk to a human agent\n"
        "0️⃣  Go back to main menu"
    )


# ─── Lead Capture ─────────────────────────────────────────────────────────────

def _start_lead_capture(conv: Conversation, lead: Lead) -> str:
    """Initiate the lead capture flow — ask for name first."""
    if lead.name and lead.email:
        # Already have full details — skip to confirmation
        return (
            f"✅ Great! We already have your details, *{lead.name}*.\n"
            "Our team will reach out to you at "
            f"{lead.email} shortly!\n\n"
            "Type *0* for main menu."
        )

    if lead.name and not lead.email:
        # Have name, missing email
        conv.state = S.LEAD_EMAIL
        return (
            f"Hey *{lead.name}*! Could you share your *email address* "
            "so we can send you the product details and pricing?"
        )

    conv.state = S.LEAD_NAME
    return (
        "✨ *Almost there!*\n\n"
        "To get you the best deal and keep you updated,\n"
        "could I start with your *name*? 😊\n\n"
        "↩️  Type *0* to skip"
    )


def _collect_name(conv: Conversation, lead: Lead, text: str) -> str:
    """Store the user's name and move to email collection."""
    if text == "0":
        return _greeting(conv, lead)

    name = text.strip().title()
    if len(name) < 2 or len(name) > 60:
        return "Please enter a valid name (2–60 characters):"

    lead.name  = name
    lead.stage = "qualified"
    _add_score(lead, "name_captured")

    conv.state = S.LEAD_EMAIL
    return (
        f"Nice to meet you, *{name}*! 😊\n\n"
        "What's your *email address*?\n"
        "We'll send you product info and exclusive offers."
    )


def _collect_email(conv: Conversation, lead: Lead, text: str) -> str:
    """Validate and store the user's email, then complete the capture flow."""
    import re

    if text == "0":
        return _greeting(conv, lead)

    email = text.strip().lower()
    if not re.match(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", email):
        return "❌ That doesn't look like a valid email. Please try again:"

    lead.email = email
    _add_score(lead, "email_captured")

    if lead.stage not in ("converted",):
        lead.stage = "interested"

    conv.state = S.BROWSE_MENU
    return (
        f"🎉 *All set, {lead.name or 'there'}!*\n\n"
        f"Our team will contact you at *{email}* with product details and pricing.\n\n"
        f"Is there anything else I can help with?\n\n"
        f"1️⃣  Browse Products\n"
        f"2️⃣  Track My Order\n"
        f"3️⃣  FAQs\n"
        f"0️⃣  Main Menu"
    )


# ─── Escalation ───────────────────────────────────────────────────────────────

def _escalate(conv: Conversation, lead: Lead) -> str:
    """Mark conversation as escalated (needs human agent)."""
    conv.state        = S.ESCALATED
    conv.is_escalated = True
    if lead.stage == "new":
        lead.stage = "qualified"

    return (
        "🙋 *Connecting you to our team!*\n\n"
        "A human agent will message you here on WhatsApp shortly.\n\n"
        "⏰ Business hours: Mon–Sat, 9 AM – 6 PM IST\n\n"
        "While you wait:\n"
        "1️⃣  Browse products\n"
        "2️⃣  Track an order\n"
        "0️⃣  Main menu"
    )


def _escalated(conv: Conversation, lead: Lead, text: str) -> str:
    """Handle messages when conversation is already escalated."""
    if text in ("0", "1", "2"):
        conv.state = S.BROWSE_MENU
        return _main_menu(conv, lead, text)
    return (
        "⏳ Our agent will be with you soon!\n\n"
        "You can still:\n"
        "1️⃣  Browse products\n"
        "2️⃣  Track order\n"
        "0️⃣  Main menu"
    )


# ─── Lead Scoring ─────────────────────────────────────────────────────────────

_SCORE_EVENTS = {
    "name_captured":   20,
    "email_captured":  20,
    "category_viewed": 10,
    "product_viewed":  20,
    "order_tracked":   10,
}


def _add_score(lead: Lead, event: str) -> None:
    """Add points to the lead's score (capped at 100)."""
    points     = _SCORE_EVENTS.get(event, 0)
    lead.score = min(100, (lead.score or 0) + points)


# ─── DB helpers ───────────────────────────────────────────────────────────────

def _get_or_create_conversation(phone: str, channel: str) -> Conversation:
    conv = (
        Conversation.query
        .filter_by(phone_number=phone, is_active=True)
        .order_by(Conversation.created_at.desc())
        .first()
    )
    if not conv:
        conv = Conversation(phone_number=phone, channel=channel, state=S.GREETING)
        db.session.add(conv)
        db.session.flush()
    return conv


def _get_or_create_lead(phone: str) -> Lead:
    lead = Lead.query.filter_by(phone_number=phone).first()
    if not lead:
        lead = Lead(phone_number=phone, stage="new", score=0)
        db.session.add(lead)
        db.session.flush()
    return lead


def _log_message(conv: Conversation, direction: str, content: str) -> None:
    db.session.add(Message(
        conversation_id=conv.id,
        direction=direction,
        content=content,
    ))


# ─── Config helpers ───────────────────────────────────────────────────────────

def _store_name() -> str:
    try:
        from flask import current_app
        return current_app.config.get("STORE_NAME", "Our Store")
    except RuntimeError:
        return "Our Store"


def _bot_name() -> str:
    try:
        from flask import current_app
        return current_app.config.get("BOT_NAME", "ShopBot")
    except RuntimeError:
        return "ShopBot"


# ─── Global trigger helpers ───────────────────────────────────────────────────

def _is_restart(text: str) -> bool:
    """Check if user wants to go back to the main menu."""
    return text.lower() in ("hi", "hello", "hey", "start", "menu", "restart", "/start", "0")