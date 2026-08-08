from __future__ import annotations

import csv
from io import StringIO
from decimal import Decimal

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models import Booking, Conversation, Customer, FAQ, Lead, MenuItem, Message, Order, User
from ..services.analytics import dashboard_metrics, daily_message_counts, leads_by_status, orders_by_status

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html")


@admin_bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("admin.login"))
    login_user(user)
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.index"))


@admin_bp.get("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        metrics=dashboard_metrics(),
        orders_by_status=orders_by_status(),
        leads_by_status=leads_by_status(),
        daily_messages=daily_message_counts(),
        recent_orders=Order.query.order_by(Order.created_at.desc()).limit(8).all(),
        recent_conversations=Conversation.query.order_by(Conversation.updated_at.desc()).limit(8).all(),
    )


@admin_bp.get("/conversations")
@login_required
def conversations():
    rows = Conversation.query.order_by(Conversation.updated_at.desc()).limit(100).all()
    return render_template("admin/conversations.html", conversations=rows)


@admin_bp.get("/conversations/<int:conversation_id>")
@login_required
def conversation_detail(conversation_id: int):
    conv = Conversation.query.get_or_404(conversation_id)
    return render_template("admin/conversation_detail.html", conversation=conv)


@admin_bp.get("/orders")
@login_required
def orders():
    rows = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=rows)


@admin_bp.post("/orders/<int:order_id>/status")
@login_required
def update_order_status(order_id: int):
    order = Order.query.get_or_404(order_id)
    status = request.form.get("status") or order.status
    allowed = {"confirmed", "preparing", "ready", "out_for_delivery", "completed", "cancelled"}
    if status in allowed:
        order.status = status
        db.session.commit()
        flash(f"Order {order.order_number} updated to {status}.", "success")
    return redirect(url_for("admin.orders"))


@admin_bp.get("/bookings")
@login_required
def bookings():
    rows = Booking.query.order_by(Booking.scheduled_for.asc()).all()
    return render_template("admin/bookings.html", bookings=rows)


@admin_bp.post("/bookings/<int:booking_id>/status")
@login_required
def update_booking_status(booking_id: int):
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get("status") or booking.status
    if status in {"confirmed", "completed", "cancelled", "no_show"}:
        booking.status = status
        db.session.commit()
        flash(f"Booking {booking.booking_number} updated.", "success")
    return redirect(url_for("admin.bookings"))


@admin_bp.get("/leads")
@login_required
def leads():
    rows = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template("admin/leads.html", leads=rows)


@admin_bp.post("/leads/<int:lead_id>/status")
@login_required
def update_lead_status(lead_id: int):
    lead = Lead.query.get_or_404(lead_id)
    status = request.form.get("status") or lead.status
    if status in {"new", "contacted", "qualified", "won", "lost"}:
        lead.status = status
        db.session.commit()
        flash("Lead updated.", "success")
    return redirect(url_for("admin.leads"))


@admin_bp.get("/menu")
@login_required
def menu_items():
    rows = MenuItem.query.order_by(MenuItem.category.asc(), MenuItem.name.asc()).all()
    return render_template("admin/menu.html", items=rows)


@admin_bp.post("/menu")
@login_required
def menu_create():
    try:
        item = MenuItem(
            sku=(request.form.get("sku") or "").strip().upper(),
            name=(request.form.get("name") or "").strip(),
            category=(request.form.get("category") or "Main").strip(),
            description=(request.form.get("description") or "").strip(),
            price=Decimal(request.form.get("price") or "0"),
            prep_time_minutes=int(request.form.get("prep_time_minutes") or 15),
            tags=(request.form.get("tags") or "").strip(),
            is_available=bool(request.form.get("is_available")),
        )
        if not item.sku or not item.name or item.price <= 0:
            raise ValueError("SKU, name and positive price are required")
        db.session.add(item)
        db.session.commit()
        flash("Menu item created.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(f"Could not create menu item: {exc}", "danger")
    return redirect(url_for("admin.menu_items"))


@admin_bp.post("/menu/<int:item_id>/toggle")
@login_required
def menu_toggle(item_id: int):
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    return redirect(url_for("admin.menu_items"))


@admin_bp.get("/faqs")
@login_required
def faqs():
    rows = FAQ.query.order_by(FAQ.category.asc(), FAQ.question.asc()).all()
    return render_template("admin/faqs.html", faqs=rows)


@admin_bp.post("/faqs")
@login_required
def faq_create():
    try:
        faq = FAQ(
            question=(request.form.get("question") or "").strip(),
            answer=(request.form.get("answer") or "").strip(),
            category=(request.form.get("category") or "general").strip(),
            keywords=(request.form.get("keywords") or "").strip(),
            is_active=bool(request.form.get("is_active")),
        )
        if not faq.question or not faq.answer:
            raise ValueError("question and answer are required")
        db.session.add(faq)
        db.session.commit()
        flash("FAQ created.", "success")
    except Exception as exc:
        db.session.rollback()
        flash(f"Could not create FAQ: {exc}", "danger")
    return redirect(url_for("admin.faqs"))


@admin_bp.post("/faqs/<int:faq_id>/toggle")
@login_required
def faq_toggle(faq_id: int):
    faq = FAQ.query.get_or_404(faq_id)
    faq.is_active = not faq.is_active
    db.session.commit()
    return redirect(url_for("admin.faqs"))


@admin_bp.get("/export/<entity>.csv")
@login_required
def export_csv(entity: str):
    output = StringIO()
    writer = csv.writer(output)
    if entity == "orders":
        writer.writerow(["order_number", "customer_phone", "status", "total", "created_at"])
        for row in Order.query.order_by(Order.created_at.desc()).all():
            writer.writerow([row.order_number, row.customer.phone, row.status, row.total_amount, row.created_at.isoformat()])
    elif entity == "leads":
        writer.writerow(["name", "phone", "email", "interest", "status", "created_at"])
        for row in Lead.query.order_by(Lead.created_at.desc()).all():
            writer.writerow([row.name, row.phone, row.email, row.interest, row.status, row.created_at.isoformat()])
    elif entity == "customers":
        writer.writerow(["name", "phone", "channel", "last_seen_at", "created_at"])
        for row in Customer.query.order_by(Customer.created_at.desc()).all():
            writer.writerow([row.name, row.phone, row.channel, row.last_seen_at.isoformat(), row.created_at.isoformat()])
    else:
        return Response("Unknown export", status=404)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={entity}.csv"})
