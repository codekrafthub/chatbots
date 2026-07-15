"""
Hospital Chatbot - FastAPI + Twilio WhatsApp version
-----------------------------------------------------
- Same reply logic as your original Flask app (kept in get_reply()).
- "/"        -> serves the web chat UI (index.html) — unchanged behaviour.
- "/chat"    -> JSON endpoint used by your existing script.js (web widget).
- "/whatsapp"-> Twilio webhook endpoint. Point your Twilio WhatsApp
                Sandbox "WHEN A MESSAGE COMES IN" URL here.

Run with:
    uvicorn main:app --reload
"""

import json

from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse

app = FastAPI(title="Hospital Chatbot")

# Static files (style.css, script.js) -> served at /static/...
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates (index.html)
templates = Jinja2Templates(directory="templates")

with open("hospital_data.json", "r", encoding="utf-8") as file:
    hospital = json.load(file)


class ChatRequest(BaseModel):
    message: str


# --------------------------------------------------------------- #
# Core reply logic (identical to the Flask version, just reused
# by both the web /chat endpoint and the /whatsapp webhook)
# --------------------------------------------------------------- #
def get_reply(raw_message: str) -> str:

    message = raw_message.lower().strip()

    # ---------------- Greetings ---------------- #
    if any(word in message for word in ["hello", "hi", "hey"]):
        reply = (
            "👋 Hello!\n\n"
            f"Welcome to {hospital['hospital_name']}.\n\n"
            "I can help you with:\n"
            "• OPD Timings\n"
            "• Emergency\n"
            "• Department Information\n"
            "• Registration\n"
            "• Pharmacy\n"
            "• Blood Bank\n"
            "• Laboratory\n"
            "• X-Ray\n"
            "• Ayushman Bharat\n"
            "• Contact Information"
        )

    # ---------------- OPD ---------------- #
    elif "opd" in message:
        reply = f"🕘 OPD Timings\n\n{hospital['opd_timings']}"

    # ---------------- Emergency ---------------- #
    elif "emergency" in message or "ambulance" in message:
        reply = hospital["emergency"]

    # ---------------- Contact ---------------- #
    elif "contact" in message or "phone" in message:
        contact = hospital["contact"]
        reply = (
            "☎ Contact Information\n\n"
            f"📞 Phone : {contact['phone']}\n"
            f"📧 Email : {contact['email']}\n"
            f"📍 Address : {contact['address']}"
        )

    # ---------------- Ayushman ---------------- #
    elif "ayushman" in message:
        reply = hospital["ayushman"]

    # ---------------- Registration ---------------- #
    elif "registration" in message or "register" in message:
        reg = hospital["registration"]
        reply = (
            "📝 Registration Counter\n\n"
            f"📍 {reg['location']}\n"
            f"🕘 {reg['timing']}\n\n"
            f"{reg['note']}"
        )

    # ---------------- Pharmacy ---------------- #
    elif "pharmacy" in message or "medicine" in message:
        pharmacy = hospital["pharmacy"]
        reply = (
            "💊 Pharmacy\n\n"
            f"📍 {pharmacy['location']}\n"
            f"🕘 {pharmacy['timing']}\n\n"
            f"{pharmacy['note']}"
        )

    # ---------------- Blood Bank ---------------- #
    elif "blood" in message:
        blood = hospital["blood_bank"]
        reply = (
            "🩸 Blood Bank\n\n"
            f"📍 {blood['location']}\n"
            f"🕘 {blood['timing']}\n\n"
            f"{blood['note']}"
        )

    # ---------------- Laboratory ---------------- #
    elif "lab" in message or "laboratory" in message or "test" in message:
        lab = hospital["laboratory"]
        reply = (
            "🧪 Laboratory\n\n"
            f"📍 {lab['location']}\n"
            f"🕘 {lab['timing']}\n\n"
            f"{lab['note']}"
        )

    # ---------------- X-Ray ---------------- #
    elif "xray" in message or "x-ray" in message:
        xray = hospital["xray"]
        reply = f"🩻 X-Ray Department\n\n📍 {xray['location']}\n🕘 {xray['timing']}"

    # ---------------- Thanks ---------------- #
    elif "thank" in message:
        reply = "😊 You're welcome!\n\nTake care and stay healthy."

    # ---------------- Departments ---------------- #
    else:
        reply = None

        for keyword, department in hospital["departments"].items():
            if keyword in message:
                reply = (
                    f"🏥 {department['name']} Department\n\n"
                    f"📍 Location : {department['location']}\n"
                    f"🕘 OPD : {department['timing']}\n\n"
                    f"📝 {department['note']}"
                )
                break

        if reply is None:
            reply = (
                "❌ Sorry, I couldn't understand your question.\n\n"
                "You can ask about:\n\n"
                "• Hello\n"
                "• OPD\n"
                "• Emergency\n"
                "• Cardiology\n"
                "• Orthopedics\n"
                "• Pediatrics\n"
                "• Registration\n"
                "• Pharmacy\n"
                "• Blood Bank\n"
                "• Laboratory\n"
                "• X-Ray\n"
                "• Ayushman Bharat\n"
                "• Contact"
            )

    return reply


# --------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------- #
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/chat")
async def chat(payload: ChatRequest):
    """Used by your existing script.js web chat widget (fetch('/chat'))."""
    reply = get_reply(payload.message)
    return JSONResponse({"reply": reply})


@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    """
    Twilio WhatsApp webhook.
    Set this URL (e.g. https://<your-ngrok-id>.ngrok-free.app/whatsapp)
    as the "WHEN A MESSAGE COMES IN" webhook in the Twilio WhatsApp
    Sandbox settings (Messaging -> Try it out -> Send a WhatsApp message).
    Twilio sends form-encoded data, not JSON, so we read Body/From as Form fields.
    """
    reply_text = get_reply(Body)

    twiml_response = MessagingResponse()
    twiml_response.message(reply_text)

    return Response(content=str(twiml_response), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
