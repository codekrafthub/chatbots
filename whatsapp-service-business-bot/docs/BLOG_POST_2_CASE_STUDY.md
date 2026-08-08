# How We Built a WhatsApp Restaurant Ordering Bot

## Problem

Restaurants and service businesses often receive the same WhatsApp questions repeatedly: menu, opening hours, delivery, booking and order status. Manual replies slow down the team.

## Solution

We built a Flask-based WhatsApp bot with a reusable architecture. The bot supports browser demo, Twilio WhatsApp Sandbox and optional Meta Cloud API.

## Key implementation decisions

- CSV-based business data for easy client onboarding
- SQL database for CRM-style records
- Deterministic state machine for reliable order and booking flows
- Admin dashboard for business visibility
- Human handoff for complex requests

## Results

The final project can handle customer FAQs, orders, booking and lead capture. It also provides analytics for conversations, leads, orders, revenue and customer interactions.
