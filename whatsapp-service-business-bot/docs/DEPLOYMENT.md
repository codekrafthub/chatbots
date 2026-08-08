# Deployment Guide

## Option 1: Render/Railway style deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn wsgi:app
```

Environment variables:

```env
APP_ENV=production
FLASK_DEBUG=0
SECRET_KEY=long-random-secret
DATABASE_URL=your_database_url
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=strong-password
PUBLIC_BASE_URL=https://your-app-domain.com
```

## Option 2: Docker

```bash
cp .env.example .env
docker compose up --build
```

## Option 3: VPS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn -b 127.0.0.1:5000 wsgi:app
```

Put Nginx in front with HTTPS and proxy to Gunicorn.

## Production database

SQLite is good for local demo. For production, use PostgreSQL.

Example:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
```

Add PostgreSQL driver to requirements if needed:

```text
psycopg[binary]
```

## Webhook URLs

Twilio:

```text
https://your-domain.com/webhook/twilio
```

Meta:

```text
https://your-domain.com/webhook/meta
```

## Production checklist

- [ ] HTTPS enabled
- [ ] Strong `SECRET_KEY`
- [ ] Strong admin password
- [ ] Database backups configured
- [ ] `FLASK_DEBUG=0`
- [ ] Twilio signature validation enabled for Twilio production
- [ ] `.env` not committed
- [ ] Admin route protected
- [ ] Customer opt-in process documented
- [ ] Message templates approved if sending business-initiated WhatsApp notifications
- [ ] Clear handoff path to human staff
- [ ] Error logs monitored
