"""
scripts/import_csv.py — Bulk CSV Importer
==========================================
Import or update records from CSV files into the database
without dropping existing data (upsert behaviour).

Supported tables:
    products      → data/products.csv
    categories    → data/categories.csv
    orders        → data/sample_orders.csv
    faqs          → data/faqs.csv

Usage:
    python scripts/import_csv.py --table products
    python scripts/import_csv.py --table all
    python scripts/import_csv.py --file my_products.csv --table products

Behaviour:
    - If record already exists (by unique key): UPDATE it
    - If record is new: INSERT it
    - Existing records NOT in the CSV are left untouched
    - Errors in individual rows are logged and skipped (no full rollback)
"""

import os
import sys
import csv
import argparse
import logging
from pathlib import Path

# ── Add project root to path so Flask app can be imported ────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DATA_DIR = PROJECT_ROOT / "data"


# ── Importers ─────────────────────────────────────────────────────────────────

def import_categories(csv_path: Path, db, models) -> tuple:
    """
    Upsert categories from CSV.
    Unique key: name
    Returns (inserted, updated) counts.
    """
    Category = models.Category
    inserted = updated = 0

    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("name", "").strip()
            if not name:
                continue

            existing = Category.query.filter_by(name=name).first()
            if existing:
                existing.emoji       = row.get("emoji", existing.emoji)
                existing.description = row.get("description", existing.description)
                updated += 1
            else:
                db.session.add(Category(
                    name=name,
                    emoji=row.get("emoji", "🛍️"),
                    description=row.get("description", ""),
                ))
                inserted += 1

    db.session.commit()
    return inserted, updated


def import_products(csv_path: Path, db, models) -> tuple:
    """
    Upsert products from CSV.
    Unique key: sku
    """
    Product  = models.Product
    Category = models.Category
    inserted = updated = 0

    with open(csv_path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            sku = row.get("sku", "").strip()
            if not sku:
                logger.warning(f"  Row {i}: missing SKU — skipped")
                continue

            try:
                # Resolve category name → FK id
                cat_name = row.get("category", "").strip()
                cat      = Category.query.filter_by(name=cat_name).first() if cat_name else None

                price = float(row.get("price", 0))

                existing = Product.query.filter_by(sku=sku).first()
                if existing:
                    existing.name        = row.get("name", existing.name)
                    existing.description = row.get("description", existing.description)
                    existing.price       = price
                    existing.category_id = cat.id if cat else existing.category_id
                    existing.in_stock    = row.get("in_stock", "true").lower() == "true"
                    existing.is_featured = row.get("is_featured", "false").lower() == "true"
                    updated += 1
                else:
                    db.session.add(Product(
                        sku=sku,
                        name=row.get("name", sku),
                        description=row.get("description", ""),
                        price=price,
                        category_id=cat.id if cat else None,
                        in_stock=row.get("in_stock", "true").lower() == "true",
                        is_featured=row.get("is_featured", "false").lower() == "true",
                    ))
                    inserted += 1

            except Exception as exc:
                logger.error(f"  Row {i} (sku={sku}): {exc} — skipped")
                db.session.rollback()
                continue

    db.session.commit()
    return inserted, updated


def import_orders(csv_path: Path, db, models) -> tuple:
    """
    Upsert orders from CSV.
    Unique key: order_id
    """
    Order    = models.Order
    inserted = updated = 0

    with open(csv_path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            order_id = row.get("order_id", "").strip()
            if not order_id:
                logger.warning(f"  Row {i}: missing order_id — skipped")
                continue

            try:
                amount   = float(row.get("amount", 0))
                existing = Order.query.filter_by(order_id=order_id).first()

                if existing:
                    existing.customer_name      = row.get("customer_name", existing.customer_name)
                    existing.customer_phone     = row.get("customer_phone", existing.customer_phone)
                    existing.product_name       = row.get("product_name", existing.product_name)
                    existing.status             = row.get("status", existing.status)
                    existing.amount             = amount
                    existing.estimated_delivery = row.get("estimated_delivery", existing.estimated_delivery)
                    updated += 1
                else:
                    db.session.add(Order(
                        order_id=order_id,
                        customer_name=row.get("customer_name", ""),
                        customer_phone=row.get("customer_phone", ""),
                        product_name=row.get("product_name", ""),
                        status=row.get("status", "Processing"),
                        amount=amount,
                        estimated_delivery=row.get("estimated_delivery", ""),
                    ))
                    inserted += 1

            except Exception as exc:
                logger.error(f"  Row {i} (order_id={order_id}): {exc} — skipped")
                db.session.rollback()
                continue

    db.session.commit()
    return inserted, updated


def import_faqs(csv_path: Path, db, models) -> tuple:
    """
    Upsert FAQs from CSV.
    Unique key: question text
    """
    FAQ      = models.FAQ
    inserted = updated = 0

    with open(csv_path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            question = row.get("question", "").strip()
            if not question:
                logger.warning(f"  Row {i}: missing question — skipped")
                continue

            try:
                existing = FAQ.query.filter_by(question=question).first()
                if existing:
                    existing.answer   = row.get("answer", existing.answer)
                    existing.category = row.get("category", existing.category)
                    existing.keywords = row.get("keywords", existing.keywords)
                    existing.priority = int(row.get("priority", existing.priority))
                    updated += 1
                else:
                    db.session.add(FAQ(
                        question=question,
                        answer=row.get("answer", ""),
                        category=row.get("category", "General"),
                        keywords=row.get("keywords", ""),
                        priority=int(row.get("priority", 0)),
                    ))
                    inserted += 1

            except Exception as exc:
                logger.error(f"  Row {i}: {exc} — skipped")
                db.session.rollback()
                continue

    db.session.commit()
    return inserted, updated


# ── Table registry ────────────────────────────────────────────────────────────

TABLE_CONFIG = {
    "categories": {
        "default_csv": DATA_DIR / "categories.csv",
        "importer":    import_categories,
    },
    "products": {
        "default_csv": DATA_DIR / "products.csv",
        "importer":    import_products,
    },
    "orders": {
        "default_csv": DATA_DIR / "sample_orders.csv",
        "importer":    import_orders,
    },
    "faqs": {
        "default_csv": DATA_DIR / "faqs.csv",
        "importer":    import_faqs,
    },
}


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Upsert records from CSV files into the database."
    )
    parser.add_argument(
        "--table",
        choices=list(TABLE_CONFIG.keys()) + ["all"],
        default="all",
        help="Which table to import (default: all)",
    )
    parser.add_argument(
        "--file",
        help="Override the default CSV file path for the chosen table",
    )
    args = parser.parse_args()

    # ── Bootstrap Flask app context ───────────────────────────────────────────
    from app import create_app
    from extensions import db
    import models

    app = create_app("development")

    tables = (
        list(TABLE_CONFIG.keys()) if args.table == "all" else [args.table]
    )

    with app.app_context():
        for table in tables:
            cfg      = TABLE_CONFIG[table]
            csv_path = Path(args.file) if args.file and len(tables) == 1 else cfg["default_csv"]

            if not csv_path.exists():
                logger.warning(f"⚠️  {csv_path} not found — skipping {table}")
                continue

            logger.info(f"📥 Importing {table} from {csv_path} ...")
            ins, upd = cfg["importer"](csv_path, db, models)
            logger.info(f"   ✅ {ins} inserted, {upd} updated")

    logger.info("✅ Import complete.")


if __name__ == "__main__":
    main()