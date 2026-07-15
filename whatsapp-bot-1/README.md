# Government Hospital Assistant — WhatsApp Chatbot

> **Client:** Government Hospital (Demo Project)  
> **Built by:** Jyotiraditya Singh  
> **Mentor:** Kapil & Apratim  
> **Timeline:** Summer Internship 2026  
> **Status:** ✅ Delivered

---

# Problem Statement

Government hospitals receive many repetitive patient queries such as OPD timings, emergency services, department information, laboratory details, blood bank availability, Ayushman Bharat information, and contact details. Responding manually takes time and increases staff workload.

---

# Solution Overview

This chatbot automates common hospital-related queries through both a website interface and WhatsApp.

Features:

- Greeting new users
- OPD timings
- Emergency information
- Department lookup
- Laboratory information
- Blood Bank information
- Ayushman Bharat information
- Contact information
- Website chatbot support
- WhatsApp chatbot support using Twilio Sandbox

---

# Architecture

```
                    WhatsApp User
                          │
                          ▼
                 Twilio WhatsApp Sandbox
                          │
                          ▼
                    FastAPI Backend
                      (main.py)
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
 Intent Detection   hospital_data.json   Website UI
                          │
                          ▼
                 Response Generation
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
     WhatsApp Response          Website Response
```

Architecture Diagram:

`docs/architecture/bot-1-architecture.png`

---

# Tech Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3 |
| Framework | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | JSON (`hospital_data.json`) |
| WhatsApp API | Twilio WhatsApp Sandbox |
| Webhook Testing | Ngrok |

---

# Local Setup

## Prerequisites

- Python 3.10+
- Twilio Account
- Ngrok
- Git

---

## Installation

```bash
git clone <repository-url>

cd whatsapp-bot-1

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Run the Project

```bash
uvicorn main:app --reload
```

or

```bash
python main.py
```

---

## Expose Localhost

```bash
ngrok http 8000
```

Copy the HTTPS URL and configure it as the Twilio WhatsApp Sandbox webhook.

---

# Environment Variables

Create a `.env` file using `.env.example`.

Example:

```
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=
NGROK_URL=
```

Do not commit `.env`.

---

# Project Structure

```
whatsapp-bot-1/
│
├── docs/
│   └── architecture/
│       ├── architecture.md
│       └── bot-1-architecture.png
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── hospital_data.json
├── main.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# Deployment

## Development

- Run FastAPI locally.
- Expose localhost using Ngrok.
- Configure the Ngrok URL in Twilio Sandbox.

---

# Testing

The following features were tested successfully on both Website and WhatsApp.

- Website Chat
- WhatsApp Chat
- OPD Timings
- Emergency
- Cardiology
- Orthopedics
- Laboratory
- Blood Bank
- Ayushman Bharat
- Contact Information

---

# Known Limitations

- Uses static JSON data.
- Twilio Sandbox is intended for development only.
- No database integration.
- No user authentication.

---

# Lessons Learned

- Integrating FastAPI with Twilio Webhooks.
- Building a responsive chatbot interface.
- Handling hospital information using structured JSON.
- Testing APIs using Ngrok.
- Deploying and validating webhook-based applications.

---

# Links

🏗️ Architecture Documentation

`docs/architecture/architecture.md`

🏗️ Architecture Diagram

`docs/architecture/bot-1-architecture.png`