# Architecture Breakdown

## One-page overview

```text
WhatsApp User / Browser Demo
          |
          v
+-----------------------+
| Flask Routes          |
| /webhook/twilio       |
| /webhook/meta         |
| /api/demo/message     |
+-----------------------+
          |
          v
+-----------------------+
| Bot Engine            |
| intent detection      |
| order state machine   |
| booking state machine |
| FAQ matching          |
| lead capture          |
+-----------------------+
          |
          v
+-----------------------+
| SQL Database          |
| customers             |
| conversations         |
| messages              |
| menu_items            |
| faqs                  |
| orders                |
| bookings              |
| leads                 |
| feedback              |
+-----------------------+
          |
          v
+-----------------------+
| Admin Dashboard       |
| analytics             |
| CRM views             |
| order management      |
| lead management       |
| CSV exports           |
+-----------------------+
```

## Main request flow

### Twilio

1. Customer sends WhatsApp message.
2. Twilio posts form data to `/webhook/twilio`.
3. Flask parses `From`, `Body`, `ProfileName` and `MessageSid`.
4. The bot stores inbound message.
5. The bot engine generates a reply.
6. Flask returns XML/TwiML with the reply.
7. Twilio sends the reply back on WhatsApp.

### Meta Cloud API

1. Meta sends JSON webhook to `/webhook/meta`.
2. Flask extracts sender phone, message id and text body.
3. Bot engine generates a reply.
4. App posts text reply to Meta Graph API `/PHONE_NUMBER_ID/messages` endpoint.

### Browser demo

1. Demo page sends JSON to `/api/demo/message`.
2. Same bot engine is used.
3. Reply is shown in the browser.

## Bot engine design

The bot uses a deterministic state machine. This is easier to explain in college and safer for WhatsApp compliance than an unrestricted general-purpose AI chatbot.

Example state object:

```json
{
  "flow": "order",
  "step": "items",
  "cart": [
    {"menu_item_id": 1, "quantity": 2}
  ]
}
```

Supported flows:

- `order`
- `booking`
- `lead`
- `feedback`

## Database design

| Table | Purpose |
|---|---|
| users | Admin login users |
| customers | WhatsApp/demo users |
| conversations | Conversation sessions |
| messages | Inbound/outbound message history |
| menu_items | Restaurant/client product catalog |
| faqs | Business FAQ automation data |
| orders | Customer orders |
| order_items | Line items in each order |
| bookings | Table reservations / appointments |
| leads | Human callback and sales opportunities |
| feedback | Customer ratings and comments |
| business_settings | Optional key-value settings |

## Why this is reusable

To convert this restaurant bot into another service bot:

- Replace `data/menu.csv` with service packages or products.
- Replace `data/faqs.csv` with client FAQs.
- Rename labels in templates if needed.
- Keep the same webhook, CRM, analytics and admin architecture.
