"""
models.py — Database Models
============================
All SQLAlchemy ORM models live here.
 
Tables
──────
AdminUser     → admin dashboard login (Flask-Login UserMixin)
Lead          → captured customer leads with pipeline stage + scoring
Conversation  → a WhatsApp chat session with one user
Message       → individual messages within a conversation
Order         → e-commerce order records (used for order-tracking feature)
Category      → top-level product groupings (Electronics, Clothing, etc.)
Product       → individual SKUs in the catalogue
FAQ           → question/answer pairs with keyword triggers
 
Lead Scoring (0–100)
─────────────────────
  name captured      → +20
  email captured     → +20
  category viewed    → +10
  product viewed     → +20
  order tracked      → +10
 
Lead Temperature
────────────────
  HOT  ≥ 70   WARM ≥ 40   COLD < 40
"""
 
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from config import Config


 
# ─── Admin ────────────────────────────────────────────────────────────────────
 
class AdminUser(UserMixin, db.Model):
    """Login user for the admin dashboard."""
    __tablename__ = "admin_users"
 
    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
 
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)
 
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
 
    def __repr__(self):
        return f"<AdminUser {self.username}>"
 
 
# ─── Lead ─────────────────────────────────────────────────────────────────────
 
class Lead(db.Model):
    """
    Captured customer lead.
 
    Stage lifecycle:
        new → qualified (name+phone) → interested (product noted) → converted (order placed)
    """
    __tablename__ = "leads"
 
    id               = db.Column(db.Integer,    primary_key=True)
    phone_number     = db.Column(db.String(20),  unique=True, nullable=False, index=True)
    name             = db.Column(db.String(100))
    email            = db.Column(db.String(120))
    product_interest = db.Column(db.String(200))   # e.g. "Electronics > Smartphones"
    stage            = db.Column(db.String(20),  default="new")
    score            = db.Column(db.Integer,     default=0)
    notes            = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow)
 
    @property
    def temperature(self) -> str:
        if self.score >= Config.LEAD_HOT_THRESHOLD:
            return "HOT"
        elif self.score >= Config.LEAD_WARM_THRESHOLD:
            return "WARM"
        return "COLD"
 
    def __repr__(self):
        return f"<Lead {self.phone_number} [{self.stage}] score={self.score}>"
 
 
# ─── Conversation + Message ───────────────────────────────────────────────────
 
class Conversation(db.Model):
    """One WhatsApp chat session. Tracks FSM state for the bot."""
    __tablename__ = "conversations"
 
    id            = db.Column(db.Integer,    primary_key=True)
    phone_number  = db.Column(db.String(20), nullable=False, index=True)
    channel       = db.Column(db.String(10), default="twilio")   # 'twilio' | 'meta'
    state         = db.Column(db.String(60), default="GREETING")  # current FSM state
    is_active     = db.Column(db.Boolean,    default=True)
    is_escalated  = db.Column(db.Boolean,    default=False)       # handed to human agent
    created_at    = db.Column(db.DateTime,   default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,   default=datetime.utcnow,
                              onupdate=datetime.utcnow)
 
    messages = db.relationship(
        "Message", backref="conversation",
        lazy="dynamic", order_by="Message.created_at"
    )
 
    @property
    def message_count(self) -> int:
        return self.messages.count()
 
    @property
    def last_message(self):
        return self.messages.order_by(Message.created_at.desc()).first()
 
    def __repr__(self):
        return f"<Conversation {self.id} [{self.phone_number}] state={self.state}>"
 
 
class Message(db.Model):
    """A single WhatsApp message (inbound or outbound)."""
    __tablename__ = "messages"
 
    id              = db.Column(db.Integer,  primary_key=True)
    conversation_id = db.Column(db.Integer,  db.ForeignKey("conversations.id"), nullable=False)
    direction       = db.Column(db.String(4), nullable=False)   # 'in' | 'out'
    content         = db.Column(db.Text,     nullable=False)
    msg_type        = db.Column(db.String(20), default="text")   # 'text' | 'image'
    created_at      = db.Column(db.DateTime,  default=datetime.utcnow)
 
    def __repr__(self):
        return f"<Message [{self.direction}] {self.content[:40]}>"
 
 
# ─── Order ────────────────────────────────────────────────────────────────────
 
class Order(db.Model):
    """
    E-commerce order record — powers the bot's 'Track My Order' feature.
 
    Status flow:
        Processing → Confirmed → Shipped → Out for Delivery → Delivered
        (also: Cancelled)
    """
    __tablename__ = "orders"
 
    id                 = db.Column(db.Integer,    primary_key=True)
    order_id           = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_phone     = db.Column(db.String(20))
    customer_name      = db.Column(db.String(100))
    product_name       = db.Column(db.String(200))
    status             = db.Column(db.String(30), default="Processing")
    amount             = db.Column(db.Float,      default=0.0)
    tracking_url       = db.Column(db.String(500))
    estimated_delivery = db.Column(db.String(50))
    created_at         = db.Column(db.DateTime,   default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime,   default=datetime.utcnow,
                                   onupdate=datetime.utcnow)
 
    def __repr__(self):
        return f"<Order {self.order_id} [{self.status}]>"
 
 
# ─── Product Catalogue ────────────────────────────────────────────────────────
 
class Category(db.Model):
    """Top-level product category (Electronics, Clothing, Home & Kitchen …)."""
    __tablename__ = "categories"
 
    id          = db.Column(db.Integer,     primary_key=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    emoji       = db.Column(db.String(10),  default="🛍️")
    description = db.Column(db.String(300))
    is_active   = db.Column(db.Boolean,     default=True)
 
    products = db.relationship("Product", backref="category", lazy="dynamic")
 
    def __repr__(self):
        return f"<Category {self.name}>"
 
 
class Product(db.Model):
    """Individual product / SKU in the catalogue."""
    __tablename__ = "products"
 
    id          = db.Column(db.Integer,     primary_key=True)
    sku         = db.Column(db.String(50),  unique=True, nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float,       nullable=False)
    category_id = db.Column(db.Integer,     db.ForeignKey("categories.id"))
    image_url   = db.Column(db.String(500))
    in_stock    = db.Column(db.Boolean,     default=True)
    is_featured = db.Column(db.Boolean,     default=False)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
 
    def __repr__(self):
        return f"<Product {self.sku}: {self.name}>"
 
 
# ─── FAQ ─────────────────────────────────────────────────────────────────────
 
class FAQ(db.Model):
    """
    Frequently asked question with keyword triggers.
    The bot finds the FAQ with the most keyword overlap with the user's message.
    """
    __tablename__ = "faqs"
 
    id       = db.Column(db.Integer,     primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer   = db.Column(db.Text,        nullable=False)
    category = db.Column(db.String(50),  default="General")
    keywords = db.Column(db.String(500))   # comma-separated trigger words
    priority = db.Column(db.Integer,     default=0)   # higher = tried first
 
    @property
    def keyword_list(self) -> list:
        if not self.keywords:
            return []
        return [k.strip().lower() for k in self.keywords.split(",")]
 
    def __repr__(self):
        return f"<FAQ [{self.category}] {self.question[:50]}>"
 
 