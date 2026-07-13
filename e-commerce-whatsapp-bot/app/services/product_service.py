### `app/services/product_service.py`

# app/services/product_service.py
# ──────────────────────────────────────────────────────────────────────────────
# Product catalog operations.
# Powers the BROWSE_PRODUCTS and VIEW_CATEGORY bot flows.
# ──────────────────────────────────────────────────────────────────────────────

from ..extensions import db
from ..models import Product


class ProductService:
    """Read/search the product catalog."""

    def get_categories(self) -> list:
        """Return sorted list of distinct active categories."""
        rows = (db.session.query(Product.category)
                .filter(Product.is_active == True, Product.category != None)
                .distinct()
                .order_by(Product.category)
                .all())
        return [r[0] for r in rows if r[0]]

    def get_by_category(self, category: str) -> list:
        """Get all active products in a category, cheapest first."""
        return (Product.query
                .filter(Product.is_active == True,
                        Product.category.ilike(category))
                .order_by(Product.price.asc())
                .all())

    def get_product(self, product_id: int) -> Product | None:
        return Product.query.filter_by(id=product_id, is_active=True).first()

    def search(self, query: str) -> list:
        """Full-text search on name and description."""
        return (Product.query
                .filter(Product.is_active == True,
                        db.or_(
                            Product.name.ilike(f'%{query}%'),
                            Product.description.ilike(f'%{query}%')
                        ))
                .limit(10)
                .all())

    def add_product(self, name, price, category,
                    description='', sku='', stock=0) -> Product:
        """Add a product to the catalog."""
        p = Product(name=name, price=price, category=category,
                    description=description, sku=sku, stock=stock)
        db.session.add(p)
        db.session.commit()
        return p