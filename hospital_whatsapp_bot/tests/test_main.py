from main import get_reply


def test_greeting():
    reply = get_reply("hello")
    assert "Hello" in reply


def test_opd():
    reply = get_reply("opd")
    assert "OPD" in reply


def test_unknown_message():
    reply = get_reply("xyzqwerty123")
    assert "couldn't understand" in reply