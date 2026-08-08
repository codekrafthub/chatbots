from __future__ import annotations

import click
from flask import Flask

from .extensions import db
from .models import User
from .services.seed import ensure_default_admin, seed_demo_analytics, seed_reference_data


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables."""
        db.create_all()
        ensure_default_admin()
        seed_reference_data()
        click.echo("Database initialized and reference data seeded.")

    @app.cli.command("seed")
    def seed_command():
        """Seed menu, FAQ and demo analytics data."""
        seed_reference_data()
        seed_demo_analytics()
        click.echo("Seed data loaded.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option("--name", default="Admin")
    def create_admin_command(email: str, password: str, name: str):
        existing = User.query.filter_by(email=email.lower()).first()
        if existing:
            click.echo("Admin already exists for this email.")
            return
        user = User(name=name, email=email.lower(), role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo("Admin created.")

    @app.cli.command("reset-db")
    @click.confirmation_option(prompt="This will delete all local data. Continue?")
    def reset_db_command():
        db.drop_all()
        db.create_all()
        ensure_default_admin()
        seed_reference_data()
        click.echo("Database reset complete.")
