# API Reference

## Public

### `GET /`

Landing page.

### `GET /demo`

Browser chat simulator.

### `POST /api/demo/message`

Request:

```json
{
  "phone": "demo:+910000000001",
  "message": "menu"
}
```

Response:

```json
{
  "reply": "..."
}
```

### `GET /health`

Response:

```json
{"status": "ok"}
```

## Twilio

### `POST /webhook/twilio`

Consumes Twilio form fields:

- `From`
- `Body`
- `ProfileName`
- `MessageSid`

Returns XML/TwiML.

## Meta

### `GET /webhook/meta`

Webhook verification endpoint.

### `POST /webhook/meta`

Consumes WhatsApp Cloud API webhook JSON and sends reply using Graph API if credentials are configured.

## Admin

- `GET /admin`
- `GET /admin/conversations`
- `GET /admin/conversations/<id>`
- `GET /admin/orders`
- `POST /admin/orders/<id>/status`
- `GET /admin/bookings`
- `POST /admin/bookings/<id>/status`
- `GET /admin/leads`
- `POST /admin/leads/<id>/status`
- `GET /admin/menu`
- `POST /admin/menu`
- `POST /admin/menu/<id>/toggle`
- `GET /admin/faqs`
- `POST /admin/faqs`
- `POST /admin/faqs/<id>/toggle`
- `GET /admin/export/orders.csv`
- `GET /admin/export/leads.csv`
- `GET /admin/export/customers.csv`
