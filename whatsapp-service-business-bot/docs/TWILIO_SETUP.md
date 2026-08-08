# Twilio WhatsApp Sandbox Setup

## Why Twilio Sandbox is best for fast demo

Twilio Sandbox lets you test WhatsApp without waiting for a production WhatsApp sender approval. This makes it ideal for a college project, MVP or portfolio demo.

## Steps

1. Create a Twilio account.
2. Open Messaging > Try it out > Send a WhatsApp message.
3. Join the sandbox by sending the shown join code to Twilio's sandbox number.
4. Run the Flask app locally:

```bash
flask --app run.py run --debug
```

5. Start ngrok:

```bash
ngrok http 5000
```

6. In Twilio Sandbox configuration, set:

```text
When a message comes in:
https://YOUR-NGROK-URL/webhook/twilio
Method: POST
```

7. Send `hi` from WhatsApp.

## Common issues

### No reply from WhatsApp

Check:

- Flask server running
- ngrok running
- Twilio webhook URL is HTTPS
- URL ends with `/webhook/twilio`
- Method is POST
- You joined the sandbox from your WhatsApp number

### Signature validation fails

For local development keep:

```env
VALIDATE_TWILIO_SIGNATURE=false
```

For production:

```env
PUBLIC_BASE_URL=https://your-real-domain.com
TWILIO_AUTH_TOKEN=your_twilio_auth_token
VALIDATE_TWILIO_SIGNATURE=true
```

`PUBLIC_BASE_URL` must exactly match the public domain Twilio calls.
