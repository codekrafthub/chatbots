"""
app/services/faq.py — FAQ Keyword Matching Service
====================================================
Finds the most relevant FAQ for a user's free-text question
using simple bag-of-words keyword overlap.

Why not NLP?
    Keyword matching is 100% offline, zero latency, and zero extra deps.
    It works surprisingly well for e-commerce support queries.
    You can upgrade to sentence-transformers later if needed.

Matching algorithm:
    1. Tokenise the user's message into lowercase words
    2. For each FAQ, count overlapping words with its keywords list
    3. Return the FAQ with the highest overlap (minimum 1 match required)
"""

import logging
from models import FAQ

logger = logging.getLogger(__name__)


def find_best_faq(user_text: str):
    """
    Search FAQs by keyword overlap with the user's message.

    Args:
        user_text: Raw message body from the user

    Returns:
        Best-matching FAQ object or None if no match found (0 overlaps)
    """
    if not user_text or not user_text.strip():
        return None

    # Tokenise: lowercase + split on whitespace/punctuation
    import re
    words = set(re.findall(r"[a-z]+", user_text.lower()))

    all_faqs   = FAQ.query.order_by(FAQ.priority.desc()).all()
    best_faq   = None
    best_score = 0

    for faq in all_faqs:
        keywords = set(faq.keyword_list)   # already lowercased by the model property
        if not keywords:
            continue

        overlap = len(words & keywords)
        if overlap > best_score:
            best_score = overlap
            best_faq   = faq

    if best_faq and best_score >= 1:
        logger.debug(f"[FAQ] Match: '{best_faq.question}' (score={best_score})")
        return best_faq

    logger.debug(f"[FAQ] No match for: '{user_text}'")
    return None


def get_faqs_by_category(category: str) -> list:
    """
    Return all FAQs in a category, sorted by priority (highest first).

    Args:
        category: e.g. 'Shipping', 'Returns', 'Payment', 'Availability'
    """
    return (
        FAQ.query
        .filter_by(category=category)
        .order_by(FAQ.priority.desc())
        .all()
    )


def get_all_categories() -> list:
    """Return a sorted list of distinct FAQ category names."""
    from extensions import db
    from sqlalchemy import distinct

    rows = db.session.query(distinct(FAQ.category)).filter(FAQ.category.isnot(None)).all()
    return sorted(r[0] for r in rows if r[0])


def get_all_faqs() -> list:
    """Return all FAQs ordered by category then priority."""
    return FAQ.query.order_by(FAQ.category, FAQ.priority.desc()).all()