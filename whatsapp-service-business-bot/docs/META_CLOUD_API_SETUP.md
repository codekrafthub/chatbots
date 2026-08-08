# Meta WhatsApp Cloud API Setup

The project includes Meta Cloud API support, but Twilio Sandbox is simpler for immediate testing.

## Webhook verification

Set your callback URL:

```text
https://your-domain.com/webhook/meta
```

Set verify token equal to `.env`:

```env
META_VERIFY_TOKEN=change-this-verify-token
```

When Meta sends a verification request, the route returns `hub.challenge` when the token matches.

## Message webhook

The POST endpoint reads this structure:

```text
entry[0].changes[0].value.messages[0].text.body
```

The generated reply is sent to:

```text
https://graph.facebook.com/{META_GRAPH_API_VERSION}/{META_PHONE_NUMBER_ID}/messages
```

## Environment variables

```env
META_ACCESS_TOKEN=your_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_GRAPH_API_VERSION=v25.0
```

## Production notes

- Use system-user/permanent token where appropriate.
- Store tokens in hosting secrets, not in GitHub.
- Subscribe to `messages` field.
- Follow WhatsApp Business Platform policies.
- Use this as a business-specific customer support bot, not as a general-purpose AI chatbot.
