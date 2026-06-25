from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

with open("hospital_data.json", "r", encoding="utf-8") as file:
    hospital = json.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    message = request.json["message"].lower().strip()

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

        reply = (
            "🕘 OPD Timings\n\n"
            f"{hospital['opd_timings']}"
        )

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

        reply = (
            "🩻 X-Ray Department\n\n"
            f"📍 {xray['location']}\n"
            f"🕘 {xray['timing']}"
        )

    # ---------------- Thanks ---------------- #

    elif "thank" in message:

        reply = (
            "😊 You're welcome!\n\n"
            "Take care and stay healthy."
        )

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

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)