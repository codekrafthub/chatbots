# WhatsApp E-Commerce Bot

A Flask-based WhatsApp Commerce Bot that enables customers to browse products, search inventory, place orders, and receive automated support directly through WhatsApp using Meta's WhatsApp Cloud API.

---

# Features

## Customer Features

* Browse product catalog
* Search products by name
* View product details
* Add products to cart
* Place orders through WhatsApp
* Track order status
* Receive order confirmations
* Automated FAQ responses

## Admin Features

* Product management
* Order management
* Customer management
* Dashboard analytics
* Inventory monitoring
* Message logs

## Technical Features

* WhatsApp Cloud API integration
* Flask application factory pattern
* Modular architecture
* Environment-based configuration
* Docker support
* Unit testing support
* Logging and monitoring
* Production deployment ready

---

# Project Structure

```text
whatsapp-bot-1/
│
├── app/
│   ├── channels/
│   │   └── whatsapp.py
│   │
│   ├── routes/
│   │   ├── admin.py
│   │   ├── customer.py
│   │   ├── products.py
│   │   └── webhook.py
│   │
│   ├── services/
│   │   ├── catalog_service.py
│   │   ├── order_service.py
│   │   ├── customer_service.py
│   │   ├── whatsapp_service.py
│   │   └── message_handler.py
│   │
│   └── __init__.py
│
├── data/
│   ├── products.json
│   ├── customers.json
│   └── orders.json
│
├── docs/
│   ├── architecture.md
│   ├── deployment-guide.md
│   └── api-reference.md
│
├── scripts/
│   ├── seed_data.py
│   └── setup.sh
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── admin/
│   └── public/
│
├── tests/
│   ├── test_routes.py
│   ├── test_services.py
│   └── test_webhook.py
│
├── .env.example
├── .gitignore
├── cli.py
├── config.py
├── extensions.py
├── models.py
├── run.py
├── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── Makefile
├── requirements.txt
└── README.md
```

---

# Architecture

```text
WhatsApp User
      │
      ▼
WhatsApp Cloud API
      │
      ▼
Webhook Endpoint
      │
      ▼
Message Handler
      │
 ┌────┼────┐
 ▼    ▼    ▼
Catalog Orders Customer
Service Service Service
      │
      ▼
 Database / JSON Storage
```

---

# Installation

## Clone Repository

```bash
git clone <repository-url>
cd whatsapp-bot-1
```

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create environment file:

```bash
cp .env.example .env
```

Example:

```env
FLASK_ENV=development
SECRET_KEY=your_secret_key

WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

DATABASE_URL=sqlite:///database.db

LOG_LEVEL=INFO
```

---

# WhatsApp Cloud API Setup

## Step 1

Create a Meta Developer Account.

## Step 2

Create a WhatsApp Business App.

## Step 3

Generate:

* Access Token
* Phone Number ID
* Verify Token

## Step 4

Configure Webhook URL:

```text
https://your-domain.com/webhook
```

---


---

# Database Setup

These commands must be run **manually once** before starting the app for the first time.
The application does not create tables or seed data automatically on startup.

## Initialise Database Tables

```bash
flask init-db
```

## Seed Sample Data

Loads sample products, categories, FAQs and orders:

```bash
flask seed-db
```

## Create Admin Login

Creates your admin dashboard credentials:

```bash
flask create-admin
```

---


# Running the Application

## Development Mode

```bash
python run.py
```

Application:

```text
http://localhost:5000
```

---

# Production Mode

Using Gunicorn:

```bash
gunicorn wsgi:app
```

---

# Docker Deployment

Build Image:

```bash
docker build -t whatsapp-bot .
```

Run Container:

```bash
docker run -p 5000:5000 whatsapp-bot
```

Using Docker Compose:

```bash
docker-compose up --build
```

---

# Database Models

## Product

```python
Product
├── id
├── name
├── category
├── description
├── price
├── stock
└── image_url
```

## Customer

```python
Customer
├── id
├── name
├── phone
├── email
└── created_at
```

## Order

```python
Order
├── id
├── customer_id
├── total_amount
├── status
└── created_at
```

---

# API Endpoints

## Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Product Catalog

```http
GET /products
```

---

## Product Details

```http
GET /products/<id>
```

---

## Webhook Verification

```http
GET /webhook
```

---

## WhatsApp Messages

```http
POST /webhook
```

---

# Supported Commands

Customers can send:

```text
Hi
```

```text
Catalog
```

```text
Products
```

```text
Search Shoes
```

```text
Order 101
```

```text
Track Order
```

```text
Help
```

---

# Testing

Run all tests:

```bash
pytest
```

Verbose:

```bash
pytest -v
```

Coverage:

```bash
pytest --cov=app
```

---

# Makefile Commands

Install dependencies:

```bash
make install
```

Run application:

```bash
make run
```

Run tests:

```bash
make test
```

Lint project:

```bash
make lint
```

---

# Logging

Application logs include:

* Incoming messages
* Outgoing messages
* API requests
* Order events
* Error traces

Log location:

```text
logs/application.log
```

---

# Security

Implemented security practices:

* Environment variables
* Token validation
* Webhook verification
* Input sanitization
* Error handling
* Secure headers

---

# CI/CD Pipeline

GitHub Actions workflow can perform:

1. Install dependencies
2. Run linting
3. Execute tests
4. Build Docker image
5. Deploy to production

---

# Deployment Targets

Supported platforms:

* Render
* Railway
* Heroku
* AWS EC2
* DigitalOcean
* Azure
* Google Cloud Platform

---

# Future Enhancements

* Payment Gateway Integration
* Razorpay Support
* Stripe Support
* Recommendation Engine
* AI Product Assistant
* Multi-language Support
* Customer Segmentation
* Inventory Forecasting

---

# Troubleshooting

## Invalid Webhook Token

Verify:

```env
WHATSAPP_VERIFY_TOKEN
```

matches Meta configuration.

## Access Token Expired

Generate a new token from Meta Developer Console.

## Port Already In Use

Change port:

```bash
flask run --port 8000
```

---

# License

MIT License

---

# Author

Devansh Verma

Civil & Infrastructure Engineering
Indian Institute of Technology Jodhpur

---

# Acknowledgements

* Meta WhatsApp Cloud API
* Flask Community
* SQLAlchemy
* Docker
* Pytest
