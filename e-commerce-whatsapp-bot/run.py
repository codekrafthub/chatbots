"""
run.py — Development Server Entry Point
========================================
Run with:  python run.py
Or:        flask run --debug

Do NOT use this in production — use wsgi.py with gunicorn instead.
"""

import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
    )