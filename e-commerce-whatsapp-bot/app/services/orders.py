"""
app/services/orders.py — Order Tracking Service
=================================================
All order-related database operations used by the bot and admin panel.

Order status lifecycle:
    Processing → Confirmed → Shipped → Out for Delivery → Delivered
    (side branch: Cancelled)

Orders are seeded from data/sample_orders.csv via `flask seed-db`,
or added manually via the admin dashboard.
"""

import logging
from models import Order
from extensions import db

logger = logging.getLogger(__name__)

# Valid status values — enforced before any DB write
VALID_STATUSES = (
    "Processing",
    "Confirmed",
    "Shipped",
    "Out for Delivery",
    "Delivered",
    "Cancelled",
)


def get_order_status(order_id: str):
    """
    Look up an order by Order ID (case-insensitive).

    Args:
        order_id: Customer-facing reference like 'ORD-1234'

    Returns:
        Order model instance or None if not found
    """
    return Order.query.filter(Order.order_id.ilike(order_id.strip())).first()


def get_orders_by_phone(phone: str) -> list:
    """Return all orders associated with a customer phone number, newest first."""
    return (
        Order.query
        .filter_by(customer_phone=phone)
        .order_by(Order.created_at.desc())
        .all()
    )


def update_order_status(order_id: str, new_status: str) -> bool:
    """
    Update the status field of an existing order.

    Args:
        order_id:   The unique order reference string
        new_status: Must be one of VALID_STATUSES

    Returns:
        True on success, False if order not found or status invalid
    """
    if new_status not in VALID_STATUSES:
        logger.warning(f"[Orders] Rejected invalid status: '{new_status}'")
        return False

    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        logger.warning(f"[Orders] Order not found: '{order_id}'")
        return False

    order.status = new_status
    db.session.commit()
    logger.info(f"[Orders] {order_id} → {new_status}")
    return True


def get_orders_summary() -> dict:
    """
    Return a dict of {status: count} for the admin dashboard.
    Also includes a 'total' key.
    """
    summary = {s: Order.query.filter_by(status=s).count() for s in VALID_STATUSES}
    summary["total"] = Order.query.count()
    return summary


def create_order(order_id: str, customer_phone: str, customer_name: str,
                 product_name: str, amount: float,
                 estimated_delivery: str = "") -> Order:
    """
    Create a new order record (used when a lead converts to a buyer).

    Args:
        order_id:           Unique order reference
        customer_phone:     Customer's WhatsApp number
        customer_name:      Customer's name
        product_name:       Product / order description
        amount:             Order value in INR
        estimated_delivery: Human-readable date string (optional)

    Returns:
        Newly created and committed Order instance
    """
    order = Order(
        order_id=order_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        product_name=product_name,
        status="Processing",
        amount=amount,
        estimated_delivery=estimated_delivery,
    )
    db.session.add(order)
    db.session.commit()
    logger.info(f"[Orders] Created order {order_id} for {customer_phone}")
    return order