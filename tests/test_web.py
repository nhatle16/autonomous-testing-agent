from fastapi.testclient import TestClient

from src.web import create_app
from tests.test_chat import FakeAgent


def _client(agent):
    return TestClient(create_app(agent))


def _send(client, text, session_id="s1"):
    return client.post("/api/chat", json={"session_id": session_id, "message": text})


# Number of messages the agent received on each call
def _message_counts(agent):
    return [len(state["messages"]) for state in agent.calls]


# The reply text is streamed back as plain text
def test_chat_streams_reply():
    response = _send(_client(FakeAgent()), "def f(): pass")

    assert response.status_code == 200
    assert response.text == "reply"


# Each turn sends the earlier turns' history to the agent
def test_chat_keeps_history_across_turns():
    agent = FakeAgent()
    client = _client(agent)
    _send(client, "one")
    _send(client, "two")

    assert _message_counts(agent) == [1, 3]


# Reset starts the session over with an empty history
def test_reset_clears_history():
    agent = FakeAgent()
    client = _client(agent)
    _send(client, "one")
    client.post("/api/reset", json={"session_id": "s1"})
    _send(client, "two")

    assert _message_counts(agent) == [1, 1]


# A failed turn reports the error and is left out of the history
def test_failed_turn_returns_error_and_is_dropped():
    agent = FakeAgent(fail_first=True)
    client = _client(agent)

    assert _send(client, "one").text == "Error invoking agent: API down"
    _send(client, "two")
    assert _message_counts(agent) == [1, 1]


# Blank messages are rejected without calling the agent
def test_empty_message_returns_400():
    agent = FakeAgent()

    assert _send(_client(agent), "  \n").status_code == 400
    assert agent.calls == []


# Different session ids never share history
def test_sessions_are_separate():
    agent = FakeAgent()
    client = _client(agent)
    _send(client, "one", session_id="a")
    _send(client, "two", session_id="b")

    assert _message_counts(agent) == [1, 1]
