from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal

from flask import current_app

from ..models import MenuItem
from .orders import money


STOPWORDS = {"i", "want", "need", "please", "add", "order", "and", "with", "one", "a", "an", "the", "for", "me"}
NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def available_items():
    return MenuItem.query.filter_by(is_available=True).order_by(MenuItem.category.asc(), MenuItem.name.asc()).all()


def format_menu(limit_per_category: int = 8) -> str:
    groups: dict[str, list[MenuItem]] = defaultdict(list)
    for item in available_items():
        groups[item.category].append(item)
    if not groups:
        return "The menu is being updated. Please try again soon."

    lines = ["🍽️ *Today's Menu*", "Reply with SKUs like `PZ01 x2, BR01 x1`, or type `order` to start."]
    for category, items in groups.items():
        lines.append(f"\n*{category}*")
        for item in items[:limit_per_category]:
            tag_text = f" ({item.tags})" if item.tags else ""
            lines.append(f"{item.sku} — {item.name}{tag_text}: {money(item.price, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}")
        if len(items) > limit_per_category:
            lines.append(f"...and {len(items) - limit_per_category} more items.")
    return "\n".join(lines)


def find_items_by_query(query: str, limit: int = 5) -> list[MenuItem]:
    normalized = normalize(query)
    tokens = {t for t in normalized.split() if t not in STOPWORDS}
    scored: list[tuple[int, MenuItem]] = []
    for item in available_items():
        haystack = normalize(" ".join([item.sku, item.name, item.category, item.description, item.tags]))
        score = 0
        if item.sku.lower() in normalized:
            score += 10
        if normalize(item.name) in normalized:
            score += 8
        score += sum(1 for token in tokens if token in haystack)
        if score:
            scored.append((score, item))
    return [item for _, item in sorted(scored, key=lambda row: row[0], reverse=True)[:limit]]


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9₹.\s-]", " ", (text or "").lower()).strip()


def parse_cart_lines(text: str) -> list[dict]:
    """Parse WhatsApp-friendly order text.

    Examples:
    - PZ01 x2, BR01 x1
    - 2 PZ01 and 1 mango lassi
    - margherita pizza
    """
    text = text or ""
    normalized = normalize(text)
    if not normalized:
        return []

    items = available_items()
    lines: dict[int, int] = {}

    for item in items:
        sku = item.sku.lower()
        sku_patterns = [
            rf"\b{re.escape(sku)}\b\s*(?:x|\*)?\s*(\d+)?",
            rf"\b(\d+)\s*(?:x|\*)?\s*{re.escape(sku)}\b",
        ]
        for pattern in sku_patterns:
            for match in re.finditer(pattern, normalized):
                groups = [g for g in match.groups() if g]
                qty = int(groups[0]) if groups else 1
                lines[item.id] = lines.get(item.id, 0) + max(1, min(qty, 20))

    for item in items:
        item_name = normalize(item.name)
        if not item_name or item.id in lines:
            continue
        if item_name in normalized:
            qty = 1
            before = normalized[: normalized.find(item_name)].split()[-3:]
            for token in reversed(before):
                if token.isdigit():
                    qty = int(token)
                    break
                if token in NUMBER_WORDS:
                    qty = NUMBER_WORDS[token]
                    break
            lines[item.id] = lines.get(item.id, 0) + max(1, min(qty, 20))
            continue
        # Partial match: at least two meaningful words from item name are present.
        words = [w for w in item_name.split() if w not in STOPWORDS and len(w) > 2]
        if words and sum(1 for w in words if w in normalized) >= min(2, len(words)):
            lines[item.id] = lines.get(item.id, 0) + 1

    return [{"menu_item_id": item_id, "quantity": qty} for item_id, qty in lines.items()]


def cart_summary(cart: list[dict]) -> tuple[str, Decimal]:
    if not cart:
        return "Your cart is empty.", Decimal("0")
    ids = [int(line["menu_item_id"]) for line in cart]
    items_by_id = {item.id: item for item in MenuItem.query.filter(MenuItem.id.in_(ids)).all()}
    lines = ["🛒 *Your Cart*"]
    subtotal = Decimal("0")
    for line in cart:
        item = items_by_id.get(int(line["menu_item_id"]))
        if not item:
            continue
        qty = int(line.get("quantity", 1))
        total = item.price * qty
        subtotal += total
        lines.append(f"{item.sku} — {item.name} x {qty}: {money(total, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}")
    lines.append(f"Subtotal: {money(subtotal, current_app.config.get('BUSINESS_CURRENCY', 'INR'))}")
    return "\n".join(lines), subtotal
