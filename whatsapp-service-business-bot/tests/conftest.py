import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="function")
def app():
    """
    Create a fresh Flask application for each test.
    """

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "WTF_CSRF_ENABLED": False,
            "LOAD_DEMO_ANALYTICS": False,
            "ADMIN_EMAIL": "admin@example.com",
            "ADMIN_PASSWORD": "password123",
        }
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client.
    """
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """
    Flask CLI runner.
    Useful for testing custom CLI commands such as:

        flask seed
        flask init-db
        flask reset-db
    """
    return app.test_cli_runner()