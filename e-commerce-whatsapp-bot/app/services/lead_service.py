### `app/services/lead_service.py`

# app/services/lead_service.py
# ──────────────────────────────────────────────────────────────────────────────
# Lead capture and CRM operations.
# Handles create/update/query for e-commerce leads.
# ──────────────────────────────────────────────────────────────────────────────

from datetime import datetime
from flask import current_app
from ..extensions import db
from ..models import Lead


class LeadService:
    """Manage e-commerce leads."""

    def create_lead(self, phone: str, name: str = '', email: str = '',
                    interest: str = '', budget: str = '',
                    source: str = 'whatsapp') -> Lead | None:
        """
        Create a new lead, or update if the phone number already exists.

        Using "upsert" logic because the same person may chat again —
        we update their info rather than creating duplicates.
        """
        try:
            existing = Lead.query.filter_by(phone=phone).first()

            if existing:
                # Update existing lead with any new info provided
                if name:     existing.name     = name
                if email:    existing.email    = email
                if interest: existing.interest = interest
                if budget:   existing.budget   = budget
                existing.updated_at = datetime.utcnow()
                db.session.commit()
                current_app.logger.info(f"Lead updated: {phone}")
                return existing
            else:
                lead = Lead(
                    phone=phone, name=name, email=email,
                    interest=interest, budget=budget,
                    source=source, status='new'
                )
                db.session.add(lead)
                db.session.commit()
                current_app.logger.info(f"New lead: {name} ({phone})")
                return lead

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Lead creation error: {e}")
            return None

    def get_by_phone(self, phone: str) -> Lead | None:
        return Lead.query.filter_by(phone=phone).first()

    def update_status(self, lead_id: int, status: str) -> bool:
        """Update lead's CRM status (new → contacted → converted → lost)."""
        valid = {'new', 'contacted', 'converted', 'lost'}
        if status not in valid:
            return False
        lead = Lead.query.get(lead_id)
        if not lead:
            return False
        lead.status     = status
        lead.updated_at = datetime.utcnow()
        db.session.commit()
        return True

    def get_recent(self, limit: int = 20) -> list:
        return Lead.query.order_by(Lead.created_at.desc()).limit(limit).all()