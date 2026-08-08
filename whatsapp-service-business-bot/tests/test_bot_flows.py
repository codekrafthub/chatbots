def send(client, text, phone="test:+910000000001"):
    return client.post(
        "/api/demo/message",
        json={"message": text, "phone": phone},
    ).get_json()["reply"]


def test_menu_reply(client):
    reply = send(client, "menu")
    assert "Today's Menu" in reply
    assert "PZ01" in reply


def test_order_flow(client):
    reply = send(client, "order")
    assert "Today's Menu" in reply

    reply = send(client, "PZ01 x2, BR01 x1")
    assert "Your Cart" in reply

    reply = send(client, "done")
    assert "delivery address" in reply.lower()

    reply = send(client, "221B Baker Street, Pune")
    assert "Payment" in reply

    reply = send(client, "cash")
    assert "Order confirmed" in reply
    assert "ORD-" in reply


def test_booking_flow(client):
    assert "booking name" in send(client, "book").lower()
    assert "date and time" in send(client, "Rohit").lower()
    assert "how many" in send(client, "tomorrow 7pm").lower()

    reply = send(client, "4")

    assert "Booking confirmed" in reply
    assert "BK-" in reply


def test_lead_flow(client):
    assert "staff" in send(client, "human").lower()

    reply = send(
        client,
        "Rohit, catering for 40 people, rohit@example.com",
    )

    assert "shared with our staff" in reply


# ---------------------------------------------------------------------
# Integration Test
# ---------------------------------------------------------------------

def test_complete_customer_journey(client):
    """
    End-to-end integration test.

    Simulates a complete customer interaction with the chatbot,
    covering greeting, ordering, booking, lead generation,
    and FAQ flow.
    """

    # Greeting
    reply = send(client, "hi")
    assert reply

    # Menu
    reply = send(client, "menu")
    assert "Today's Menu" in reply

    # Order flow
    reply = send(client, "order")
    assert "Today's Menu" in reply

    reply = send(client, "PZ01 x2, BR01 x1")
    assert "Your Cart" in reply

    reply = send(client, "done")
    assert "delivery" in reply.lower()

    reply = send(client, "221B Baker Street, Pune")
    assert "payment" in reply.lower()

    reply = send(client, "cash")
    assert "Order confirmed" in reply
    assert "ORD-" in reply

    # Booking flow
    reply = send(client, "book")
    assert "booking" in reply.lower()

    reply = send(client, "Rohit")
    assert "date" in reply.lower()

    reply = send(client, "tomorrow 7pm")
    assert "how many" in reply.lower()

    reply = send(client, "4")
    assert "Booking confirmed" in reply

    # Human escalation
    reply = send(client, "human")
    assert "staff" in reply.lower()

    reply = send(
        client,
        "Rohit, corporate lunch for 30 people, rohit@example.com",
    )

    assert "shared with our staff" in reply

    # FAQ
    reply = send(client, "timing")
    assert reply