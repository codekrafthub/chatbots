# Government Hospital Assistant — WhatsApp Chatbot

> **Client:** Government Hospital (Demo Project)  
> **Built by:** Jyotiraditya Singh  
> **Mentors:** Kapil & Apratim  
> **Timeline:** Summer Internship 2026  
> **Status:** Delivered

## Problem Statement

Government hospitals receive many repetitive patient queries such as OPD timings, emergency services, department information, laboratory details, blood bank information, Ayushman Bharat information, and contact details.

Handling these common queries manually can increase staff workload and response time.

## Solution Overview

This project provides a Government Hospital Assistant chatbot that responds to common hospital-related queries through:

- A browser-based chat interface
- A WhatsApp interface using the Twilio WhatsApp Sandbox

The chatbot uses structured hospital information stored in `hospital_data.json` and a reusable `get_reply()` function in `main.py`.

## Features

- Greeting and welcome message
- OPD timings
- Emergency and ambulance information
- Department information
- Keyword-based department guidance
- Registration information
- Pharmacy information
- Blood Bank information
- Laboratory information
- X-Ray information
- Ayushman Bharat information
- Hospital contact information
- Browser-based chatbot UI
- WhatsApp chatbot through Twilio Sandbox
- JSON-based hospital data
- Automated tests

## Architecture

```text
                         WhatsApp User
                              |
                              v
                  Twilio WhatsApp Sandbox
                              |
                              v
                       FastAPI Backend
                           main.py
                              |
                              v
                         get_reply()
                              |
                              v
                      hospital_data.json
                              |
                              v
                       Generated Reply


                         Browser User
                              |
                              v
                        Web Chat UI
                              |
                              v
                         POST /chat
                              |
                              v
                       FastAPI Backend
                              |
                              v
                         get_reply()
                              |
                              v
                       Generated Reply
```

Architecture documentation:

`docs/architecture.md`

Architecture diagram:

`docs/bot-1-architecture.png`

## Tech Stack

| Layer | Technology |
|---|---|
| Programming Language | Python 3 |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | JSON |
| WhatsApp Integration | Twilio WhatsApp Sandbox |
| Webhook Testing | Ngrok |
| Testing | Pytest |

# Local Setup

## Prerequisites

- Python 3.10 or newer
- Git
- Twilio account for WhatsApp testing
- Ngrok for local webhook testing

## 1. Clone the Repository

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd hospital_whatsapp_bot
```

If the repository has already been cloned, simply enter:

```bash
cd hospital_whatsapp_bot
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

## 4. Environment Configuration

The project includes an example environment file:

```text
.env.example
```

Create a local `.env` file based on `.env.example` and add your own credentials where required.

Example:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

HOST=0.0.0.0
PORT=8000

HOSPITAL_DATA_FILE=hospital_data.json

NGROK_URL=https://your-ngrok-url.ngrok-free.app

LOG_LEVEL=INFO
```

Do not commit real credentials or secrets to GitHub.

The `.env.example` file contains placeholders only.

# Running the Web Chatbot

From inside the `hospital_whatsapp_bot` directory:

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

Open the address in a browser to use the web chatbot.

## API Routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Serves the web chat interface |
| POST | `/chat` | Handles web chat messages |
| POST | `/whatsapp` | Handles Twilio WhatsApp webhook messages |

# WhatsApp Integration

The WhatsApp webhook is implemented at:

```text
POST /whatsapp
```

The webhook receives the incoming WhatsApp message from Twilio, passes the message to the same `get_reply()` function used by the web chatbot, and returns a TwiML response.

## 1. Start FastAPI

```bash
uvicorn main:app --reload
```

## 2. Start Ngrok

In another terminal:

```bash
ngrok http 8000
```

Ngrok will provide an HTTPS URL similar to:

```text
https://your-ngrok-url.ngrok-free.app
```

## 3. Configure the Twilio Sandbox

Set the Twilio WhatsApp Sandbox **WHEN A MESSAGE COMES IN** webhook URL to:

```text
https://your-ngrok-url.ngrok-free.app/whatsapp
```

Use the HTTP method configured for the Twilio webhook.

## 4. Test WhatsApp

Send a WhatsApp message to the configured Twilio Sandbox number.

The request is received by:

```text
/whatsapp
```

and the chatbot generates the response through:

```text
get_reply()
```

# Chatbot Logic

The main chatbot logic is implemented in:

```text
main.py
```

The reusable response function is:

```text
get_reply()
```

Both interfaces use the same response logic:

```text
Web Chat
   |
   v
 /chat
   |
   v
get_reply()
   |
   v
Response


WhatsApp
   |
   v
/whatsapp
   |
   v
get_reply()
   |
   v
Twilio Response
```

This keeps the chatbot response logic centralized.

# Hospital Data

Hospital information is stored in:

```text
hospital_data.json
```

The data includes information such as:

- Hospital name
- OPD timings
- Emergency information
- Contact information
- Registration
- Pharmacy
- Blood Bank
- Laboratory
- X-Ray
- Ayushman Bharat
- Departments

Keeping this information in JSON separates hospital-specific data from the chatbot logic.

# Project Structure

```text
hospital_whatsapp_bot/
│
├── docs/
│   ├── architecture.md
│   └── bot-1-architecture.png
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── tests/
│   └── test_main.py
│
├── .env.example
├── hospital_data.json
├── main.py
├── README.md
└── requirements.txt
```

Development-only files such as virtual environments and Python cache files should not be committed.

# Testing

Automated tests are located in:

```text
tests/test_main.py
```

Run the tests from the `hospital_whatsapp_bot` directory:

```bash
python -m pytest
```

The current test suite covers:

- Greeting response
- OPD response
- Unknown-message fallback

A successful test run should report all tests passing.

# API Examples

## `POST /chat`

Example request:

```json
{
  "message": "opd"
}
```

Example response:

```json
{
  "reply": "..."
}
```

## `POST /whatsapp`

The endpoint accepts the form-encoded message fields sent by Twilio and returns a TwiML XML response.

# Known Limitations

- Hospital information is stored in a static JSON file.
- Twilio WhatsApp Sandbox is intended for development/testing.
- No database is currently used.
- No user authentication is implemented.
- The chatbot uses rule/keyword-based response logic rather than an AI/LLM model.
- Ngrok is used for local webhook development rather than production deployment.

# Development

For development with automatic reload:

```bash
uvicorn main:app --reload
```

For running without automatic reload:

```bash
uvicorn main:app
```

# Lessons Learned

- Building a FastAPI backend for a chatbot
- Integrating a Twilio WhatsApp webhook
- Handling form-encoded webhook requests
- Creating a browser-based chatbot interface
- Separating application data from chatbot logic using JSON
- Using Ngrok for local webhook development
- Writing automated tests with Pytest
- Structuring a small chatbot project for maintainability

# Documentation

Architecture documentation:

`docs/architecture.md`

Architecture diagram:

`docs/bot-1-architecture.png`