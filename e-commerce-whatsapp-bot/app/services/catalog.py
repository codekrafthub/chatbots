"""
app/services/catalog.py — Product Catalogue Service
=====================================================
All product and category read operations.
The bot uses these to power the Browse Products flow;
the admin dashboard uses them for the catalogue management page.

Products and categories are seeded from:
    data/categories.csv
    data/products.csv
"""

from models import Category, Product


# ─── Categories ──────────────────────────────────────────────────────────────

def get_active_categories() -> list:
    """
    Return all active categories, sorted alphabetically by name.
    Used by the bot to display the category menu.
    """
    return (
        Category.query
        .filter_by(is_active=True)
        .order_by(Category.name)
        .all()
    )


def get_category_by_id(category_id: int):
    """Fetch a single category by primary key. Returns None if not found."""
    return Category.query.get(category_id)


# ─── Products ─────────────────────────────────────────────────────────────────

def get_products_by_category(category_id: int, in_stock_only: bool = False) -> list:
    """
    Return products belonging to a category.

    Args:
        category_id:  Primary key of the category
        in_stock_only: If True, filter out out-of-stock products

    Returns:
        List of Product instances, ordered by name
    """
    query = Product.query.filter_by(category_id=category_id)

    if in_stock_only:
        query = query.filter_by(in_stock=True)

    return query.order_by(Product.name).all()


def get_product_by_id(product_id: int):
    """Fetch a single product by primary key."""
    return Product.query.get(product_id)


def get_product_by_sku(sku: str):
    """Fetch a product by its SKU code (case-insensitive)."""
    return Product.query.filter(Product.sku.ilike(sku.strip())).first()


def get_featured_products(limit: int = 5) -> list:
    """
    Return in-stock featured products (is_featured=True), up to `limit`.
    Used on the landing page and as suggestions in the bot.
    """
    return (
        Product.query
        .filter_by(is_featured=True, in_stock=True)
        .order_by(Product.name)
        .limit(limit)
        .all()
    )


def search_products(query_text: str) -> list:
    """
    Simple ILIKE search across product name and description.

    Args:
        query_text: Search keyword(s) from the user

    Returns:
        Matching Product instances, ordered by name
    """
    pattern = f"%{query_text.strip()}%"
    return (
        Product.query
        .filter(
            (Product.name.ilike(pattern)) |
            (Product.description.ilike(pattern))
        )
        .order_by(Product.name)
        .all()
    )


def get_catalogue_stats() -> dict:
    """Return high-level catalogue statistics for the admin dashboard."""
    total     = Product.query.count()
    in_stock  = Product.query.filter_by(in_stock=True).count()
    featured  = Product.query.filter_by(is_featured=True).count()
    cats      = Category.query.filter_by(is_active=True).count()

    return {
        "total_products":   total,
        "in_stock":         in_stock,
        "out_of_stock":     total - in_stock,
        "featured":         featured,
        "active_categories": cats,
    }