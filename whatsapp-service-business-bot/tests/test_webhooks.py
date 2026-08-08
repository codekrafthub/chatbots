def test_twilio_webhook_returns_twiml(client):
    response = client.post("/webhook/twilio", data={"From": "whatsapp:+9100000000", "Body": "menu", "ProfileName": "Tester"})
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    assert b"Response" in response.data
    assert b"PZ01" in response.data


def test_meta_verify(client, app):
    token = app.config["META_VERIFY_TOKEN"]
    response = client.get(f"/webhook/meta?hub.mode=subscribe&hub.verify_token={token}&hub.challenge=12345")
    assert response.status_code == 200
    assert response.data == b"12345"


def test_health(client):
    response = client.get("/health")
    assert response.get_json()["status"] == "ok"
