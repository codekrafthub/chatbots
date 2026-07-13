"""
app/services/seed.py — Database Seeder
=======================================
Populates the database with demo data for development and portfolio showcase.
Called via the Flask CLI command:  flask seed-db

Seed order (respects FK dependencies):
    1. AdminUser   (no deps)
    2. Category    (no deps)
    3. Product     (depends on Category)
    4. Order       (no deps — standalone records)
    5. FAQ         (no deps)

All seeders are idempotent — they skip rows that already exist.
Source CSV files live in the data/ folder at the project root.
"""

import csv
import os
import logging

logger = logging.getLogger(__name__)

# Absolute path to the data/ directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def seed_all():
    """Run all seeders in dependency order."""
    logger.info("🌱 Starting database seed...")
    seed_admin()
    seed_categories()
    seed_products()
    seed_orders()
    seed_faqs()
    logger.info("✅ Database seeding complete.")


# ─── Admin User ───────────────────────────────────────────────────────────────

def seed_admin():
    """Create the default admin user if one doesn't already exist."""
    from flask import current_app
    from extensions import db
    from models import AdminUser

    username = current_app.config.get("ADMIN_USERNAME", "admin")
    password = current_app.config.get("ADMIN_PASSWORD", "admin123")

    if AdminUser.query.filter_by(username=username).first():
        logger.info(f"  Admin '{username}' already exists — skipped.")
        return

    user = AdminUser(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    logger.info(f"  ✅ Admin user '{username}' created.")


# ─── Categories ───────────────────────────────────────────────────────────────

def seed_categories():
    """Seed from data/categories.csv — columns: name, emoji, description."""
    from extensions import db
    from models import Category

    path = os.path.join(DATA_DIR, "categories.csv")
    if not os.path.exists(path):
        logger.warning(f"  ⚠️  {path} not found — categories skipped.")
        return

    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if Category.query.filter_by(name=row["name"]).first():
                continue
            db.session.add(Category(
                name=row["name"],
                emoji=row.get("emoji", "🛍️"),
                description=row.get("description", ""),
            ))

    db.session.commit()
    logger.info("  ✅ Categories seeded.")


# ─── Products ─────────────────────────────────────────────────────────────────

def seed_products():
    """
    Seed from data/products.csv.
    Required columns: sku, name, price, category
    Optional columns: description, in_stock, is_featured
    """
    from extensions import db
    from models import Product, Category

    path = os.path.join(DATA_DIR, "products.csv")
    if not os.path.exists(path):
        logger.warning(f"  ⚠️  {path} not found — products skipped.")
        return

    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if Product.query.filter_by(sku=row["sku"]).first():
                continue

            # Resolve category name → FK
            cat = Category.query.filter_by(name=row.get("category", "")).first()

            db.session.add(Product(
                sku=row["sku"],
                name=row["name"],
                description=row.get("description", ""),
                price=float(row.get("price", 0)),
                category_id=cat.id if cat else None,
                in_stock=row.get("in_stock", "true").lower() == "true",
                is_featured=row.get("is_featured", "false").lower() == "true",
            ))

    db.session.commit()
    logger.info("  ✅ Products seeded.")


# ─── Orders ───────────────────────────────────────────────────────────────────

def seed_orders():
    """
    Seed from data/sample_orders.csv.
    Required: order_id, customer_name, product_name, status, amount
    Optional: customer_phone, estimated_delivery
    """
    from extensions import db
    from models import Order

    path = os.path.join(DATA_DIR, "sample_orders.csv")
    if not os.path.exists(path):
        logger.warning(f"  ⚠️  {path} not found — orders skipped.")
        return

    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if Order.query.filter_by(order_id=row["order_id"]).first():
                continue

            db.session.add(Order(
                order_id=row["order_id"],
                customer_phone=row.get("customer_phone", ""),
                customer_name=row.get("customer_name", ""),
                product_name=row.get("product_name", ""),
                status=row.get("status", "Processing"),
                amount=float(row.get("amount", 0)),
                estimated_delivery=row.get("estimated_delivery", ""),
            ))

    db.session.commit()
    logger.info("  ✅ Orders seeded.")


# ─── FAQs ────────────────────────────────────────────────────────────────────

def seed_faqs():
    """
    Seed from data/faqs.csv.
    Required: question, answer, category, keywords
    Optional: priority (integer, default 0)
    """
    from extensions import db
    from models import FAQ

    path = os.path.join(DATA_DIR, "faqs.csv")
    if not os.path.exists(path):
        logger.warning(f"  ⚠️  {path} not found — FAQs skipped.")
        return

    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if FAQ.query.filter_by(question=row["question"]).first():
                continue

            db.session.add(FAQ(
                question=row["question"],
                answer=row["answer"],
                category=row.get("category", "General"),
                keywords=row.get("keywords", ""),
                priority=int(row.get("priority", 0)),
            ))

    db.session.commit()
    logger.info("  ✅ FAQs seeded.")