"""Import menu or FAQ CSV files into the database.

Usage:
    flask --app run.py shell
    >>> from scripts.import_csv import import_menu_csv, import_faq_csv
    >>> import_menu_csv('data/menu.csv')
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from app.extensions import db
from app.models import FAQ, MenuItem


def import_menu_csv(path: str) -> int:
    count = 0
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            sku = row["sku"].strip().upper()
            item = MenuItem.query.filter_by(sku=sku).first() or MenuItem(sku=sku)
            item.name = row["name"].strip()
            item.category = row["category"].strip()
            item.description = row.get("description", "").strip()
            item.price = Decimal(row["price"].strip())
            item.prep_time_minutes = int(row.get("prep_time_minutes") or 15)
            item.tags = row.get("tags", "").strip()
            item.is_available = row.get("is_available", "true").lower() != "false"
            db.session.add(item)
            count += 1
    db.session.commit()
    return count


def import_faq_csv(path: str) -> int:
    count = 0
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            question = row["question"].strip()
            faq = FAQ.query.filter_by(question=question).first() or FAQ(question=question)
            faq.answer = row["answer"].strip()
            faq.category = row.get("category", "general").strip() or "general"
            faq.keywords = row.get("keywords", "").strip()
            faq.is_active = row.get("is_active", "true").lower() != "false"
            db.session.add(faq)
            count += 1
    db.session.commit()
    return count
