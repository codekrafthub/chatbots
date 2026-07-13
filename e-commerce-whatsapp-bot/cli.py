"""
cli.py — Flask CLI Commands
============================
Custom management commands registered on the Flask app.

Usage:
    flask init-db          Create all tables from SQLAlchemy models
    flask seed-db          Populate tables with demo/starter data
    flask drop-db          Drop all tables (⚠️  destructive!)
    flask create-admin     Create or reset the admin user
    flask reset-demo       init-db + seed-db in one step (quick dev reset)
"""

import click
from flask import Flask


def register_commands(app: Flask) -> None:
    """Attach all CLI commands to the given Flask app instance."""

    # ── init-db ───────────────────────────────────────────────────────────────

    @app.cli.command("init-db")
    def init_db():
        """Create all database tables (safe to run multiple times)."""
        from extensions import db
        import models  # noqa: F401 — ensures all models are registered

        with app.app_context():
            db.create_all()
            click.secho("✅ Database tables created.", fg="green")

    # ── seed-db ───────────────────────────────────────────────────────────────

    @app.cli.command("seed-db")
    def seed_db():
        """Populate the database with demo data from the data/ CSV files."""
        from app.services.seed import seed_all

        with app.app_context():
            seed_all()
            click.secho("✅ Database seeded.", fg="green")

    # ── drop-db ───────────────────────────────────────────────────────────────

    @app.cli.command("drop-db")
    @click.confirmation_option(prompt="⚠️  This will DELETE all data. Continue?")
    def drop_db():
        """Drop every table — useful for a clean restart in development."""
        from extensions import db

        with app.app_context():
            db.drop_all()
            click.secho("🗑️  All tables dropped.", fg="yellow")

    # ── reset-demo ────────────────────────────────────────────────────────────

    @app.cli.command("reset-demo")
    def reset_demo():
        """
        Drop + recreate + seed the database in one command.
        Perfect for resetting a demo environment quickly.
        """
        from extensions import db
        from app.services.seed import seed_all
        import models  # noqa: F401

        with app.app_context():
            click.echo("Dropping tables…")
            db.drop_all()
            click.echo("Creating tables…")
            db.create_all()
            click.echo("Seeding data…")
            seed_all()
            click.secho("✅ Demo environment reset.", fg="green")

    # ── create-admin ─────────────────────────────────────────────────────────

    @app.cli.command("create-admin")
    @click.option("--username", prompt=True,  help="Admin username")
    @click.option("--password", prompt=True,  hide_input=True,
                  confirmation_prompt=True, help="Admin password")
    def create_admin(username: str, password: str):
        """Create or overwrite the admin dashboard user."""
        from extensions import db
        from models import AdminUser

        with app.app_context():
            user = AdminUser.query.filter_by(username=username).first()
            if user:
                user.set_password(password)
                click.echo(f"Password updated for '{username}'.")
            else:
                user = AdminUser(username=username)
                user.set_password(password)
                db.session.add(user)
                click.echo(f"Admin '{username}' created.")
            db.session.commit()
            click.secho("✅ Done.", fg="green")

    # ── show-routes ───────────────────────────────────────────────────────────

    @app.cli.command("show-routes")
    def show_routes():
        """Print all registered URL rules — helpful for debugging."""
        import urllib
        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        click.echo(f"\n{'Rule':<45} {'Methods':<20} Endpoint")
        click.echo("-" * 80)
        for rule in rules:
            methods = ", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            click.echo(f"{rule.rule:<45} {methods:<20} {rule.endpoint}")