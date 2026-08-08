# Understanding WhatsApp Chatbot Architecture

A WhatsApp chatbot has four main parts: the messaging provider, webhook server, bot logic and database.

When a customer sends a message, WhatsApp sends the message to a provider such as Twilio or Meta Cloud API. The provider sends an HTTP webhook request to our Flask application. Flask extracts the sender phone number and message text, then passes it to the bot engine.

The bot engine decides what to do. For a restaurant bot, it can show the menu, collect order items, ask for address and payment method, create a booking, answer FAQs, or create a lead for staff follow-up.

The database stores customers, conversations, messages, menu items, FAQs, orders, bookings and leads. The admin dashboard reads this database and shows useful analytics such as conversations, lead conversions, customer interactions and order revenue.

This architecture is reusable because only the business data changes from client to client.
