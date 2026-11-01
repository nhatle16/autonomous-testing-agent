from langchain_core.messages import AIMessage

from src.chat import main, read_message


# Simulate keyboard input
def _inputs(*lines):
    # Create an iterator over the provided lines
    it = iter(lines)

    # Fake input() to read from the iterator
    def input_fn():
        try:
            return next(it)
        except StopIteration:
            raise EOFError from None

    return input_fn

# Define a fake agent class to simulate the agent, no actual API calls are made
class FakeAgent:
    def __init__(self, fail_first=False):
        self.calls = []
        self.fail_first = fail_first

    def invoke(self, state):
        self.calls.append(state)
        # Simulate an API failure on the first call
        if self.fail_first and len(self.calls) == 1:
            raise RuntimeError("API down")
        return {"messages": state["messages"] + [AIMessage(content="reply")]}


# Number of messages the agent received on each call
def _message_counts(agent):
    return [len(state["messages"]) for state in agent.calls]


# Lines typed before /send come back as one message joined by newlines
def test_read_messages_joins_lines_until_send():
    assert read_message(_inputs("def f():", "    pass", "/send")) == "def f():\n    pass"


# A command on the first line is returned as the command, ignoring spaces
def test_read_message_returns_command_on_first_line():
    assert read_message(_inputs("/reset")) == "/reset"
    assert read_message(_inputs("  /quit  ")) == "/quit"


# A command after the first line is kept as ordinary text
def test_read_message_keeps_command_after_first_line_as_text():
    assert read_message(_inputs("hello", "/quit", "/send")) == "hello\n/quit"


# Ctrl-D partway through a message still sends what was typed
def test_read_message_sends_typed_text_on_eof():
    assert read_message(_inputs("hello")) == "hello"


# Ctrl-D with nothing typed quits
def test_read_message_returns_quit_on_eof_without_text():
    assert read_message(_inputs()) == "/quit"


# Each turn sends the earlier messages and replies along with the new message
def test_main_keeps_history_across_turns(capsys):
    agent = FakeAgent()

    main(agent=agent, input_fn=_inputs("first", "/send", "second", "/send", "/quit"))

    # Turn 2 gets: first, reply, second
    assert _message_counts(agent) == [1, 3]
    assert agent.calls[1]["messages"][-1].content == "second"
    assert capsys.readouterr().out.count("reply") == 2


# /reset clears the history, so the next turn starts from one message
def test_main_reset_clears_history(capsys):
    agent = FakeAgent()

    main(agent=agent, input_fn=_inputs("first", "/send", "/reset", "second", "/send", "/quit"))

    assert _message_counts(agent) == [1, 1]
    assert "Conversation reset." in capsys.readouterr().out


# An empty or blank message is not sent to the agent
def test_main_skips_empty_messages():
    agent = FakeAgent()

    main(agent=agent, input_fn=_inputs("/send", "   ", "/send", "/quit"))

    assert agent.calls == []


# A failed agent call prints the error, and the next turn still works without the failed one
def test_main_keeps_running_after_agent_error(capsys):
    agent = FakeAgent(fail_first=True)

    main(agent=agent, input_fn=_inputs("first", "/send", "second", "/send", "/quit"))

    assert _message_counts(agent) == [1, 1]
    out = capsys.readouterr().out
    assert "Error invoking agent: API down" in out
    assert "reply" in out


# Ctrl-D sends the unsent text, then ends the session
def test_main_quits_on_eof():
    agent = FakeAgent()

    main(agent=agent, input_fn=_inputs("hello"))

    assert _message_counts(agent) == [1]