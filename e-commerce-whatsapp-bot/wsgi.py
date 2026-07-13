"""
wsgi.py — Production WSGI Entry Point
======================================
Used by gunicorn in production:
    gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2

Also used by Heroku via the Procfile:
    web: gunicorn wsgi:app
"""

import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "production"))