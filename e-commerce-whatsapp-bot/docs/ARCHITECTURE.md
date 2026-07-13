# E-Commerce WhatsApp Chatbot — Architecture

## 1. System Overview

This is a **Flask-based WhatsApp chatbot** for e-commerce businesses.
It lets customers browse products, track orders, get FAQ answers, and
share their contact details — all without leaving WhatsApp.

```
Customer (WhatsApp)
       │
       │  sends a message
       ▼
 Meta Cloud API  ──or──  Twilio Sandbox
       │                       │
       └──────────┬────────────┘
                  │  HTTP POST (webhook)
                  ▼
         Flask App  /webhook/meta  or  /webhook/twilio
                  │
                  ▼
         bot.handle_message()   ← CORE FSM ENGINE
                  │
         ┌────────┴────────┐
         │                 │
      services/         models.py
    catalog.py          (SQLAlchemy)
    orders.py                │
    faq.py                   ▼
    analytics.py          SQLite (dev)
    seed.py            PostgreSQL (prod)
         │
         ▼
    reply string
         │
         ▼
 Channel adapter sends reply back to WhatsApp
```

---

## 2. Directory Layout

```
ecommerce-whatsapp-bot/
│
├── app/
│   ├── channels/          # WhatsApp channel adapters
│   │   ├── meta.py        # Meta Cloud API (production)
│   │   └── twilio.py      # Twilio sandbox (development)
│   │
│   ├── routes/            # Flask Blueprints
│   │   ├── admin.py       # /admin/* — password-protected dashboard
│   │   ├── public.py      # / and /demo — public-facing pages
│   │   └── webhooks.py    # /webhook/meta and /webhook/twilio
│   │
│   └── services/          # Business logic (no Flask imports here)
│       ├── analytics.py   # Dashboard KPI aggregation
│       ├── bot.py         # ★ FSM engine — core of the chatbot
│       ├── catalog.py     # Product and category queries
│       ├── faq.py         # Keyword-matching FAQ lookup
│       ├── orders.py      # Order tracking queries
│       └── seed.py        # CSV → database seeder
│
├── data/                  # Seed CSV files
│   ├── categories.csv
│   ├── products.csv
│   ├── sample_orders.csv
│   └── faqs.csv
│
├── docs/                  # Documentation
│   └── ARCHITECTURE.md    # ← you are here
│
├── scripts/               # Standalone utility scripts
│   ├── backup_sqlite.py   # Timestamped DB backup
│   └── import_csv.py      # Bulk CSV importer
│
├── static/
│   ├── css/styles.css     # Public page styles
│   └── js/demo.js         # Browser demo widget JS
│
├── templates/
│   ├── admin/             # Admin dashboard Jinja2 templates
│   │   ├── layout.html    # Base layout with sidebar
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── leads.html
│   │   ├── conversations.html
│   │   ├── conversation_detail.html
│   │   ├── orders.html
│   │   ├── catalog.html
│   │   └── faqs.html
│   └── public/            # Public-facing templates
│       ├── base.html
│       ├── index.html     # Landing page
│       └── demo.html      # Interactive browser demo
│
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── test_bot_flows.py  # FSM unit tests
│   └── test_webhooks.py   # Webhook integration tests
│
├── config.py              # Dev / prod / test configuration
├── extensions.py          # Flask extension singletons (db, migrate, login)
├── models.py              # SQLAlchemy ORM models
├── cli.py                 # Flask CLI commands (init-db, seed-db …)
├── run.py                 # Development server entry point
├── wsgi.py                # Production WSGI entry point (gunicorn)
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── Procfile               # Heroku deployment
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## 3. Bot FSM (Finite State Machine)

The bot is a **state machine** — each conversation has a `state` field
in the database. Every incoming message is processed based on the
current state.

```
         ┌──────────────────────────────────────────────────────────┐
         │           Global trigger: "hi / hello / menu / 0"       │
         │                  resets to GREETING from any state       │
         └──────────────────────────────────────────────────────────┘

  GREETING ──(auto)──► BROWSE_MENU
                             │
              ┌──────────────┼──────────────┬───────────────┐
              │"1"           │"2"           │"3"            │"4"
              ▼              ▼              ▼               ▼
      BROWSE_CATEGORY   TRACK_ORDER       FAQ           ESCALATED
              │              │              │
              │(pick cat)     │(enter ID)   │(keyword / topic)
              ▼              ▼              ▼
    BROWSE_PRODUCT:<id>  ─► reply      ─► answer or BROWSE_MENU
              │
              │(pick product)
              ▼
    PRODUCT_ACTION:<pid>:<cid>
              │
     ┌────────┴────────┐
     │"1" / "3"        │"2"
     ▼                 ▼
  LEAD_NAME ──► LEAD_EMAIL   BROWSE_CATEGORY
```

### FSM States

| State | Description |
|-------|-------------|
| `GREETING` | Welcome message + main menu |
| `BROWSE_MENU` | Waiting for 1 / 2 / 3 / 4 |
| `BROWSE_CATEGORY` | Waiting for category number |
| `BROWSE_PRODUCT:<cat_id>` | Waiting for product number in a category |
| `PRODUCT_ACTION:<pid>:<cid>` | After viewing a product — buy / browse / share details |
| `TRACK_ORDER` | Waiting for Order ID input |
| `FAQ` | Waiting for question text or topic number |
| `LEAD_NAME` | Collecting customer name |
| `LEAD_EMAIL` | Collecting customer email |
| `ESCALATED` | Conversation routed to human agent |

---

## 4. Lead Scoring

Every engagement event adds points to the lead's score (0–100).

| Event | Points |
|-------|--------|
| Name captured | +20 |
| Email captured | +20 |
| Category browsed | +10 |
| Product viewed | +20 |
| Order tracked | +10 |

**Temperature classification:**

| Score | Temperature |
|-------|-------------|
| ≥ 70 | 🔴 HOT |
| ≥ 40 | 🟠 WARM |
| < 40 | 🔵 COLD |

---

## 5. Database Models

```
AdminUser          Lead               Conversation
─────────          ────               ────────────
id                 id                 id
username           phone_number       phone_number
password_hash      name               channel
created_at         email              state
                   product_interest   is_active
                   stage              is_escalated
                   score              created_at
                   notes              updated_at
                   created_at
                   updated_at

Message            Order              Category
───────            ─────              ────────
id                 id                 id
conversation_id    order_id           name
direction          customer_phone     emoji
content            customer_name      description
msg_type           product_name       is_active
created_at         status
                   amount             Product
                   tracking_url       ───────
                   estimated_delivery id
                   created_at         sku
                   updated_at         name
                                      description
FAQ                                   price
───                                   category_id
id                                    in_stock
question                              is_featured
answer                                image_url
category                              created_at
keywords
priority
```

---

## 6. WhatsApp Channel Adapters

Two adapters are provided — swap between them via the `CHANNEL` env var.

### Twilio (Development / Sandbox)
- No business verification needed
- Free sandbox — join by sending a WhatsApp message to the sandbox number
- Webhook: `POST /webhook/twilio`
- Payload: form-encoded (`From`, `Body`)

### Meta Cloud API (Production)
- Requires Facebook Business Verification
- Free — no per-message cost at low volumes
- Webhook: `GET /webhook/meta` (verification) + `POST /webhook/meta` (messages)
- Payload: JSON with nested `entry[].changes[].value.messages[]`

---

## 7. Request Lifecycle

```
1. Customer sends WhatsApp message
2. Platform (Meta / Twilio) sends HTTP POST to Flask webhook
3. Channel adapter parses payload → (phone, text)
4. bot.handle_message(phone, text, channel) is called
5. FSM looks up or creates Conversation + Lead in DB
6. Inbound message is logged (Message table)
7. Current state + text → correct handler function
8. Handler updates state, updates lead score, returns reply string
9. Reply is logged (Message table)
10. DB session committed
11. Channel adapter sends reply to WhatsApp
12. Flask returns HTTP 200 to platform
```

---

## 8. Admin Dashboard Routes

| URL | Page |
|-----|------|
| `/admin/` | KPI dashboard with Chart.js charts |
| `/admin/leads` | Lead table — filter by stage, temperature, search |
| `/admin/conversations` | Paginated conversation list |
| `/admin/conversations/<id>` | Full chat transcript |
| `/admin/orders` | Order tracking — filter by status, inline update |
| `/admin/catalog` | Product catalogue by category |
| `/admin/faqs` | FAQ management — view and delete |
| `/admin/login` | Login form |
| `/admin/logout` | Session logout |

---

## 9. Deployment

### Local Development
```bash
python run.py
# or
flask run --debug
```

### Docker
```bash
docker-compose up --build
```

### Heroku
```bash
git push heroku main
heroku run flask init-db
heroku run flask seed-db
```

### Environment Variables
See `.env.example` for the full list.
Critical vars: `SECRET_KEY`, `DATABASE_URL`, `CHANNEL`,
and either Twilio or Meta credentials depending on channel.