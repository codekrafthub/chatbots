from __future__ import annotations

from pathlib import Path

from flask import Flask

from .extensions import db, login_manager


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object("config.Config")

    if config_overrides:
        app.config.update(config_overrides)

    # Ensure instance folder exists
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes.public import public_bp
    from .routes.webhooks import webhooks_bp
    from .routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(webhooks_bp)
    app.register_blueprint(admin_bp)

    # Register CLI commands
    from .cli import register_cli_commands

    register_cli_commands(app)

    # Create database tables only.
    # Demo/reference data should NOT be seeded automatically.
    # Use the Flask CLI command instead:
    #
    #     flask seed
    #
    with app.app_context():
        db.create_all()

    return app