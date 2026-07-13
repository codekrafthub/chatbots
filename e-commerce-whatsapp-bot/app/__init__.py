"""
app/__init__.py — Flask Application Factory
============================================
create_app() is the entry point for the Flask app.
Using the factory pattern lets us swap configs easily
(dev vs prod vs test) and avoids circular imports.
 
Call order:
    run.py / wsgi.py → create_app(env) → init extensions
                                        → register blueprints
                                        → return app
"""
 
import os
from flask import Flask
from config import config_map
from extensions import db, migrate, login_manager
 
 
def create_app(env: str = None) -> Flask:
    """
    Create and configure the Flask application.
 
    Args:
        env: Config key — 'development', 'production', or 'testing'.
             Falls back to FLASK_ENV environment variable, then 'default'.
 
    Returns:
        Fully configured Flask application instance.
    """
    if env is None:
        env = os.environ.get("FLASK_ENV", "default")
 
    # ── Instantiate Flask (templates and static are at project root) ──────────
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )
 
    # ── Load config object ────────────────────────────────────────────────────
    app.config.from_object(config_map.get(env, config_map["default"]))
 
    # ── Initialise extensions (binds them to this app instance) ──────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
 
    # ── Flask-Login user loader ───────────────────────────────────────────────
    from models import AdminUser  # imported here to avoid circular import
 
    @login_manager.user_loader
    def load_user(user_id: str):
        return AdminUser.query.get(int(user_id))
 
    # ── Register Blueprints ───────────────────────────────────────────────────
    from app.routes.webhooks import webhooks_bp
    from app.routes.admin    import admin_bp
    from app.routes.public   import public_bp
 
    app.register_blueprint(webhooks_bp, url_prefix="/webhook")
    app.register_blueprint(admin_bp,    url_prefix="/admin")
    app.register_blueprint(public_bp,   url_prefix="/")
 
    # ── Register CLI commands ─────────────────────────────────────────────────
    from cli import register_commands
    register_commands(app)
 
    return app
 