# E-Commerce WhatsApp Bot

A production-ready WhatsApp-based e-commerce chatbot built using Python, Flask, and WhatsApp Cloud API. The project enables customers to browse products, search inventory, place orders, and receive automated support directly through WhatsApp.

## Repository Structure

```text
.
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   ├── deployment-guide.md
│   └── user-guide.md
├── whatsapp-bot-1/
│   ├── app/
│   ├── templates/
│   ├── static/
│   ├── tests/
│   ├── data/
│   ├── run.py
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

## Features

* WhatsApp Cloud API integration
* Product catalog browsing
* Product search functionality
* Order placement workflow
* Customer support automation
* Web dashboard support
* Docker deployment support
* Environment-based configuration
* Automated testing setup

## Technology Stack

### Backend

* Python 3.10+
* Flask
* SQLAlchemy
* WhatsApp Cloud API

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Deployment

* Docker
* Docker Compose
* Gunicorn
* Render / Railway / AWS / VPS

## Quick Start

### Clone Repository

```bash
git clone <repository-url>
cd ecommerce-whatsapp-bot
```

### Navigate to Application

```bash
cd whatsapp-bot-1
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Update all required environment variables.

### Run Application

```bash
python run.py
```

## Documentation

Detailed documentation is available in the `docs/` directory.

| Document            | Description             |
| ------------------- | ----------------------- |
| architecture.md     | System architecture     |
| api-reference.md    | API documentation       |
| deployment-guide.md | Deployment instructions |
| user-guide.md       | End-user guide          |

## Testing

Run all tests:

```bash
pytest
```

Generate coverage report:

```bash
pytest --cov=app
```

## Deployment

Docker deployment:

```bash
docker-compose up --build
```

Production deployment:

```bash
gunicorn wsgi:app
```

## CI/CD

GitHub Actions can be configured to:

* Run unit tests
* Perform linting
* Build Docker images
* Deploy automatically

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Create a Pull Request.

## License

This project is licensed under the MIT License.

## Authors

Developed as part of the WhatsApp Commerce Automation Project.
