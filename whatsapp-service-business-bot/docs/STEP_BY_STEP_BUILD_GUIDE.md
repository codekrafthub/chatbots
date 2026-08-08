# Complete Step-by-Step Build Guide

This guide is written so you can build the project file-by-file or understand every part after receiving the complete zip.

## Phase 1: Understand the project

Your project is a **Service Business Customer Support Bot**. The restaurant ordering bot is used as the demo business. The same architecture can be reused for salons, coaching institutes, consultants, repair services, clinics, real estate agents and local service providers.

The project has five layers:

1. WhatsApp/web/demo input
2. Flask routes and webhooks
3. Bot decision engine
4. Database and business records
5. Admin dashboard and analytics

## Phase 2: Create local environment

```bash
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
.venv\Scripts\Activate.ps1    # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env
flask --app run.py init-db
flask --app run.py run --debug
```

## Phase 3: Test without WhatsApp

Open:

```text
http://127.0.0.1:5000/demo
```

Test:

```text
hi
menu
order
PZ01 x2, BR01 x1
done
MG Road, Pune
cash
book
Rohit Kumar
tomorrow 7pm
4
human
Rohit, catering for 30 people
```

## Phase 4: Check database records

Open:

```text
http://127.0.0.1:5000/admin
```

Login using credentials from `.env`. Confirm:

- Conversations are stored
- Messages are stored
- Orders are created
- Bookings are created
- Leads are created
- Analytics cards update

## Phase 5: Connect Twilio WhatsApp Sandbox

1. Start Flask server.
2. Start ngrok:

```bash
ngrok http 5000
```

3. Copy the HTTPS forwarding URL.
4. In Twilio WhatsApp Sandbox, set webhook:

```text
https://your-ngrok-url/webhook/twilio
```

5. Send WhatsApp message:

```text
menu
```

6. Check `/admin/conversations`.

## Phase 6: Customize for any client

Edit:

```text
.env
BUSINESS_NAME=
BUSINESS_PHONE=
BUSINESS_ADDRESS=
BUSINESS_OPENING_HOURS=
```

Edit CSV files:

```text
data/menu.csv
data/faqs.csv
data/service_catalog.csv
```

Then reset local database:

```bash
flask --app run.py reset-db
```

## Phase 7: Deploy

Production settings:

```env
APP_ENV=production
FLASK_DEBUG=0
SECRET_KEY=long-random-key
DATABASE_URL=postgresql+psycopg://...
PUBLIC_BASE_URL=https://your-domain.com
VALIDATE_TWILIO_SIGNATURE=true
```

Deploy using Gunicorn:

```bash
gunicorn wsgi:app
```

## Phase 8: Final project execution checklist

- [ ] App starts locally
- [ ] Browser demo works
- [ ] Admin login works
- [ ] Menu data visible
- [ ] FAQ automation works
- [ ] Order flow creates order
- [ ] Booking flow creates booking
- [ ] Lead flow creates lead
- [ ] Analytics dashboard updates
- [ ] CSV export works
- [ ] Twilio webhook configured
- [ ] WhatsApp screenshot captured
- [ ] Test suite passes
- [ ] README and docs uploaded to GitHub
