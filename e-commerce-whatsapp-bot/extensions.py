"""
extensions.py — Flask Extension Instances
==========================================
Instantiates all Flask extensions ONCE here so they can be imported
by models.py and app/__init__.py without causing circular imports.

Pattern:
    extensions.py   → creates db, migrate, login_manager
    models.py       → imports db from extensions
    app/__init__.py → calls db.init_app(app), then imports models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate    import Migrate
from flask_login      import LoginManager

# ── Database ORM ─────────────────────────────────────────────────────────────
db = SQLAlchemy()

# ── Database migrations (Alembic wrapper) ────────────────────────────────────
migrate = Migrate()

# ── Admin dashboard session management ───────────────────────────────────────
login_manager = LoginManager()
login_manager.login_view         = "admin.login"        # Redirects here if not logged in
login_manager.login_message      = "Please log in to access the admin panel."
login_manager.login_message_category = "warning"
