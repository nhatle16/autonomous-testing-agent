from langchain_core.messages import AIMessage

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
