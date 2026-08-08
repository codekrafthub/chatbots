# WhatsApp Service Business Customer Support Bot

A production-ready Flask-based **WhatsApp Service Business Customer Support Bot** designed for restaurants and other service businesses. This project demonstrates how to build a scalable WhatsApp chatbot capable of handling customer conversations, orders, bookings, FAQs, lead generation, analytics, and administration through a modern web interface.

The project is suitable for:

- Academic projects
- Portfolio demonstrations
- Internship submissions
- Client demos
- Small business automation

The application supports three interaction modes:

1. **Browser Demo Chat** – Test the complete chatbot without WhatsApp credentials.
2. **Twilio WhatsApp Sandbox** – Quick WhatsApp integration for development and demonstrations.
3. **Meta WhatsApp Cloud API** – Production-ready adapter for Meta's official WhatsApp Business API.

> **Note:** This chatbot is intentionally designed as a **business-specific customer support assistant**, not as a general-purpose AI chatbot. All conversation flows are tailored towards restaurant/service business operations.

---

# Features

## Customer Features

- Greeting and welcome flow
- Interactive restaurant menu browsing
- Food ordering workflow
- Delivery or pickup selection
- Payment method selection
- Order confirmation
- Order tracking
- Table reservation
- Appointment booking
- Frequently Asked Questions
- Human staff escalation
- Lead capture
- Customer feedback collection
- Browser-based chatbot simulator

---

## Admin Features

- Secure administrator login
- Password hashing
- Analytics dashboard
- Revenue analytics
- Order management
- Booking management
- Customer management
- Lead management
- Conversation history
- Menu management
- FAQ management
- CSV export functionality

---

## Engineering Features

- Flask Application Factory Pattern
- SQLAlchemy ORM
- SQLite support
- PostgreSQL support through `DATABASE_URL`
- Twilio Webhook integration
- Meta WhatsApp Cloud API integration
- Secure webhook handling
- Docker support
- Docker Compose
- Procfile
- Makefile
- Production deployment guides
- Automated testing
- Modular project architecture

---

# Project Structure

```text
whatsapp-service-business-bot/
├── app/
│   ├── channels/
│   │   ├── meta.py
│   │   ├── twilio.py
│   │   └── __init__.py
│   │
│   ├── routes/
│   │   ├── admin.py
│   │   ├── public.py
│   │   └── webhooks.py
│   │
│   ├── services/
│   │   ├── analytics.py
│   │   ├── bot_engine.py
│   │   ├── faq.py
│   │   ├── menu.py
│   │   ├── orders.py
│   │   └── seed.py
│   │
│   ├── templates/
│   ├── static/
│   ├── extensions.py
│   ├── models.py
│   └── __init__.py
│
├── data/
├── docs/
├── scripts/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── Procfile
├── requirements.txt
├── run.py
└── wsgi.py
```

---

# Quick Start

## 1. Create Virtual Environment

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS

```bash
source .venv/bin/activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Create Environment File

Linux/macOS

```bash
cp .env.example .env
```

Windows PowerShell

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure at least:

```env
SECRET_KEY=make-this-long-and-random
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeMe@12345
BUSINESS_NAME=Spice Garden Restaurant
DATABASE_URL=sqlite:///servicebot.sqlite3
```

---

## 4. Initialize Database

The application automatically creates the required database tables during startup.

**Demo or reference data is NOT automatically inserted.**

This prevents production databases from being polluted after application restarts.

To manually insert demo/reference data:

```bash
flask --app run.py seed
```

To initialize only the database schema:

```bash
flask --app run.py init-db
```

---

## 5. Start the Application

```bash
flask --app run.py run --debug
```

Open your browser:

- Home Page: `http://127.0.0.1:5000/`
- Browser Demo: `http://127.0.0.1:5000/demo`
- Admin Dashboard: `http://127.0.0.1:5000/admin`

Administrator credentials are created **only** when running:

```bash
flask --app run.py seed
```

Credentials are taken from your `.env` file.

Example:

```text
admin@example.com
ChangeMe@12345
```

---

# Demo Script

Suggested demonstration flow:

1. hi
2. menu
3. order
4. PZ01 x2, BR01 x1
5. done
6. MG Road, Pune
7. cash
8. status ORD-XXXXXX
9. book
10. Rohit Kumar
11. tomorrow 7pm
12. 4
13. human
14. Rohit, corporate lunch for 30 people
15. Open `/admin`
16. Show analytics dashboard

---

# Twilio WhatsApp Sandbox Setup

1. Create a Twilio account.
2. Open the WhatsApp Sandbox.
3. Join the sandbox using the code provided by Twilio.
4. Expose your local application using ngrok:

```bash
ngrok http 5000
```

Configure the incoming webhook URL:

```text
https://YOUR-NGROK-DOMAIN.ngrok-free.app/webhook/twilio
```

Method:

```text
POST
```

Production configuration:

```env
PUBLIC_BASE_URL=https://your-domain.com
TWILIO_AUTH_TOKEN=your_token
VALIDATE_TWILIO_SIGNATURE=true
```

> **Security Recommendation:** Keep `VALIDATE_TWILIO_SIGNATURE=true` in production. Disable it only during local development if necessary.

---

# Meta WhatsApp Cloud API Setup

Meta Cloud API support is optional but included for production deployments.

1. Create a Meta Developer App.
2. Add the WhatsApp product.
3. Configure the webhook callback URL:

```text
https://your-domain.com/webhook/meta
```

4. Configure the verification token:

```env
META_VERIFY_TOKEN=change-this-verify-token
```

5. Subscribe to the **messages** webhook field.

6. Configure production credentials:

```env
META_ACCESS_TOKEN=your_meta_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_GRAPH_API_VERSION=v25.0
```

---
# Data Management

The project ships with sample datasets that allow the chatbot to be demonstrated immediately after setup.

Included datasets:

- `data/menu.csv` – Restaurant menu items, categories, prices, SKUs and tags.
- `data/faqs.csv` – Frequently asked questions and responses.
- `data/service_catalog.csv` – Services or appointments offered by the business.
- `data/sample_orders.csv` – Example order dataset used for analytics demonstrations.

---

## Production Note

Demo data is **not automatically inserted** when the application starts.

This prevents production databases from being polluted after application restarts or deployments.

To intentionally populate demo/reference data, run:

```bash
flask --app run.py seed
```

If you only want an empty database schema:

```bash
flask --app run.py init-db
```

---

## Adding a New Client

To adapt this chatbot for another business:

1. Replace the menu dataset (`menu.csv`).
2. Replace the FAQ dataset (`faqs.csv`).
3. Update business information in `.env`.
4. Import your datasets.
5. Test the Browser Demo.
6. Configure Twilio or Meta webhook.
7. Deploy the application.

---

## Database Reset

For a clean local rebuild:

```bash
flask --app run.py reset-db
```

After resetting:

```bash
flask --app run.py seed
```

---

# Running Tests

Run the complete automated test suite:

```bash
pytest -q
```

Expected output:

```text
All tests passed.
```

The test suite covers:

- Bot conversation flow
- FAQ responses
- Order workflow
- Booking workflow
- Webhook endpoints
- Database operations
- Analytics functionality

---

# Using Makefile

A Makefile is included to simplify common development tasks.

Available commands:

```bash
make install
make run
make seed
make test
make lint
```

To see every supported command:

```bash
make help
```

Using the Makefile keeps development commands consistent across contributors.

---

# Docker

Create the environment configuration:

```bash
cp .env.example .env
```

Build the application:

```bash
docker compose build
```

Run the application:

```bash
docker compose up
```

Or build and run in a single command:

```bash
docker compose up --build
```

Stop all running containers:

```bash
docker compose down
```

Visit:

```text
http://localhost:5000
```

---

# Deployment

This application can be deployed to any platform that supports Python web applications.

Supported platforms include:

- Render
- Railway
- Fly.io
- Docker
- VPS (Gunicorn + Nginx)
- Azure App Service
- AWS EC2
- DigitalOcean
- Google Cloud Run

---

## Production Checklist

Before deployment ensure the following:

- Generate a strong `SECRET_KEY`.
- Use a secure administrator password.
- Switch from SQLite to PostgreSQL.
- Configure `DATABASE_URL`.
- Configure `PUBLIC_BASE_URL` with your HTTPS domain.
- Twilio webhook signature validation should remain enabled in production.
- Configure Meta Cloud API credentials if using Meta.
- Use HTTPS for all webhook endpoints.
- Never commit `.env` to version control.
- Regularly back up the production database.
- Follow WhatsApp Business Platform policies.
- Remove demo datasets before production deployment if not required.

For complete deployment instructions, refer to:

```text
docs/DEPLOYMENT.md
```

---
# Project Demonstration Checklist

For project evaluation, internship submission, or portfolio presentation, the following assets are recommended:

- GitHub repository containing the complete source code.
- Browser Demo screenshots.
- Twilio Sandbox configuration screenshots.
- WhatsApp chatbot conversation screenshots.
- Administrator dashboard screenshots.
- Analytics dashboard screenshots.
- Architecture diagram (`docs/ARCHITECTURE.md`).
- Deployment documentation (`docs/DEPLOYMENT.md`).
- Dataset documentation (`docs/DATASETS.md`).
- Test execution screenshot (`pytest -q`).
- Case study (`docs/CASE_STUDY_TEMPLATE.md`).

---

# Repository Structure Summary

The repository contains everything required to deploy, extend, and demonstrate the chatbot.

- Source code
- Documentation
- Database models
- Sample datasets
- Automated tests
- Docker configuration
- Deployment guides
- Development utilities
- Browser demo
- WhatsApp integrations

No external proprietary software is required to evaluate the project.

---

# Security

Security was considered throughout the development of this project.

## Production Recommendations

- Keep `VALIDATE_TWILIO_SIGNATURE=true` in production.
- Never commit `.env` files to version control.
- Never expose API keys or access tokens.
- Use HTTPS for all webhook endpoints.
- Configure `PUBLIC_BASE_URL` correctly before deployment.
- Store credentials using environment variables.
- Use a strong `SECRET_KEY`.
- Use strong administrator passwords.
- Regularly back up the production database.
- Rotate API credentials periodically.

---

# Project Highlights

This project demonstrates several software engineering best practices, including:

- Flask Application Factory Pattern
- Modular architecture
- Blueprint-based routing
- SQLAlchemy ORM
- Production-ready configuration
- Secure webhook validation
- Database abstraction
- Environment-based configuration
- Docker support
- Automated testing
- Analytics dashboard
- Browser simulator
- Twilio integration
- Meta Cloud API integration
- CSV-driven business data
- Scalable channel abstraction

---

# Future Improvements

Possible future enhancements include:

- Multi-language chatbot support.
- AI-powered FAQ answering using LLMs.
- Voice message processing.
- Image recognition.
- Payment gateway integration.
- Inventory management.
- Customer loyalty program.
- Google Maps integration.
- Live delivery tracking.
- Multi-business support.
- Redis caching.
- Background task processing with Celery.
- Kubernetes deployment.
- CI/CD pipelines.
- Monitoring using Prometheus and Grafana.

---

# Technologies Used

Backend

- Python
- Flask
- SQLAlchemy
- Jinja2

Database

- SQLite
- PostgreSQL

WhatsApp

- Twilio WhatsApp Sandbox
- Meta WhatsApp Cloud API

Deployment

- Docker
- Docker Compose
- Gunicorn
- Nginx

Testing

- pytest

---

# Learning Outcomes

This project demonstrates practical knowledge of:

- REST API development
- WhatsApp Business integrations
- Database design
- Authentication
- Secure webhook handling
- Production deployment
- Docker
- Testing
- Software architecture
- Modular Flask applications

---

# Acknowledgements

This project was developed as part of an internship and educational learning experience to demonstrate production-style software engineering practices for service business automation.

Special thanks to the mentors and reviewers whose feedback helped improve the project's architecture, security, documentation, and deployment readiness.

---

# License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.