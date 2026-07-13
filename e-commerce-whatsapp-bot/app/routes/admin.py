"""
app/routes/admin.py — Admin Dashboard Routes
=============================================
All routes for the password-protected admin panel.

Pages:
    /admin/              → Dashboard (KPI cards + charts)
    /admin/leads         → Lead pipeline with filter + search
    /admin/conversations → WhatsApp conversation list
    /admin/conversations/<id> → Full chat transcript
    /admin/orders        → Order tracking management
    /admin/catalog       → Product catalogue view
    /admin/faqs          → FAQ management (view + delete)
    /admin/login         → Login form
    /admin/logout        → Logout

All pages except login/logout are protected by @login_required.
"""

import logging
from datetime import datetime, timedelta
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import AdminUser, Lead, Conversation, Message, Order, Product, Category, FAQ

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


# ─── Auth ─────────────────────────────────────────────────────────────────────

@admin_bp.get("/login")
@admin_bp.post("/login")
def login():
    """Login page — redirect to dashboard if already authenticated."""
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next") or url_for("admin.dashboard")
            flash("Logged in successfully!", "success")
            return redirect(next_page)

        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@admin_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.get("/")
@admin_bp.get("/dashboard")
@login_required
def dashboard():
    """
    Main analytics overview.
    Fetches KPI counts and recent activity for the dashboard cards.
    """
    from app.services.analytics import (
        get_daily_message_counts, get_lead_funnel,
        get_conversion_rate, get_top_product_interests, get_summary_stats,
    )

    stats            = get_summary_stats()
    lead_funnel      = get_lead_funnel()
    daily_messages   = get_daily_message_counts(days=7)
    top_interests    = get_top_product_interests(limit=5)
    recent_leads     = Lead.query.order_by(Lead.created_at.desc()).limit(8).all()

    # Lead temperature breakdown for pie chart
    all_leads  = Lead.query.all()
    temp_data  = {
        "HOT":  sum(1 for l in all_leads if l.temperature == "HOT"),
        "WARM": sum(1 for l in all_leads if l.temperature == "WARM"),
        "COLD": sum(1 for l in all_leads if l.temperature == "COLD"),
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        lead_funnel=lead_funnel,
        daily_messages=daily_messages,
        top_interests=top_interests,
        recent_leads=recent_leads,
        temp_data=temp_data,
    )


# ─── Leads ────────────────────────────────────────────────────────────────────

@admin_bp.get("/leads")
@login_required
def leads():
    """Lead management table with stage + temperature filtering and text search."""
    stage  = request.args.get("stage",  "")
    temp   = request.args.get("temp",   "")
    search = request.args.get("search", "").strip()

    query = Lead.query

    if stage:
        query = query.filter_by(stage=stage)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(like)) |
            (Lead.phone_number.ilike(like)) |
            (Lead.email.ilike(like))
        )

    all_leads = query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()

    # Temperature filter is a computed property, can't be done in SQL easily
    if temp:
        all_leads = [l for l in all_leads if l.temperature == temp.upper()]

    return render_template(
        "admin/leads.html",
        leads=all_leads,
        filter_stage=stage,
        filter_temp=temp,
        search=search,
    )


@admin_bp.post("/leads/<int:lead_id>/update")
@login_required
def update_lead(lead_id: int):
    """Update a lead's stage and notes (form POST)."""
    lead = Lead.query.get_or_404(lead_id)
    lead.stage = request.form.get("stage", lead.stage)
    lead.notes = request.form.get("notes", lead.notes)
    db.session.commit()
    flash(f"Lead {lead.name or lead.phone_number} updated.", "success")
    return redirect(url_for("admin.leads"))


# ─── Conversations ────────────────────────────────────────────────────────────

@admin_bp.get("/conversations")
@login_required
def conversations():
    """Paginated list of all WhatsApp conversations."""
    page  = request.args.get("page", 1, type=int)
    convs = (
        Conversation.query
        .order_by(Conversation.updated_at.desc())
        .paginate(page=page, per_page=20, error_out=False)
    )
    return render_template("admin/conversation.html", conversations=convs)


@admin_bp.get("/conversations/<int:conv_id>")
@login_required
def conversation_detail(conv_id: int):
    """Full message transcript for one conversation."""
    conv = Conversation.query.get_or_404(conv_id)
    msgs = conv.messages.order_by(Message.created_at.asc()).all()
    lead = Lead.query.filter_by(phone_number=conv.phone_number).first()
    return render_template(
        "admin/conversation_detail.html",
        conversation=conv,
        messages=msgs,
        lead=lead,
    )


# ─── Orders ──────────────────────────────────────────────────────────────────

@admin_bp.get("/orders")
@login_required
def orders():
    """Order list with optional status filter."""
    status     = request.args.get("status", "")
    query      = Order.query
    if status:
        query = query.filter_by(status=status)
    all_orders = query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=all_orders, filter_status=status)


@admin_bp.post("/orders/<int:order_id>/status")
@login_required
def update_order_status(order_id: int):
    """Update the shipping status of an order."""
    order        = Order.query.get_or_404(order_id)
    order.status = request.form.get("status", order.status)
    db.session.commit()
    flash(f"Order {order.order_id} updated to '{order.status}'.", "success")
    return redirect(url_for("admin.orders"))


# ─── Catalogue ────────────────────────────────────────────────────────────────

@admin_bp.get("/catalog")
@login_required
def catalog():
    """Product catalogue view with category filter."""
    cat_id     = request.args.get("category", type=int)
    query      = Product.query
    if cat_id:
        query = query.filter_by(category_id=cat_id)
    products   = query.order_by(Product.name).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
    return render_template(
        "admin/catalog.html",
        products=products,
        categories=categories,
        filter_category=cat_id,
    )


# ─── FAQs ────────────────────────────────────────────────────────────────────

@admin_bp.get("/faqs")
@login_required
def faqs():
    """FAQ list grouped by category."""
    all_faqs = FAQ.query.order_by(FAQ.category, FAQ.priority.desc()).all()
    return render_template("admin/faqs.html", faqs=all_faqs)


@admin_bp.post("/faqs/<int:faq_id>/delete")
@login_required
def delete_faq(faq_id: int):
    """Delete a FAQ entry."""
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash("FAQ deleted.", "success")
    return redirect(url_for("admin.faqs"))