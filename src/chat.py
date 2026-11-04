import itertools
import os
import sys
import threading
import uuid
from contextlib import contextmanager

from dotenv import load_dotenv
from langchain.messages import HumanMessage

from src.agent import build_agent

COMMANDS = ("/reset", "/quit")


def read_message(input_fn=input) -> str:
    """Read lines until a /send line and return the lines joined;
    return /reset or /quit if typed as the first line."""
    lines = []
    try:
        while True:
            line = input_fn()
            # A command typed on its own in the first line
            if not lines and line.strip() in COMMANDS:
                return line.strip()
            # End of message
            if line.strip() == "/send":
                return "\n".join(lines)
            lines.append(line)  # add ordinary text
    except EOFError:
        # End of input (Ctrl-D): send what was typed; the next call then returns /quit
        return "\n".join(lines) if lines else "/quit"


@contextmanager
def loading(text="Reasoning"):
    """Animate "<text>." / ".." / "..." on one line until the block finishes, then clear it."""
    # Only animate if stdout is an interactive terminal
    if not sys.stdout.isatty():
        yield
        return

    stop = threading.Event()

    def animate():
        for dots in itertools.cycle([".", "..", "..."]):
            # \r returns to the line start; \033[K clears leftover characters
            print(f"\r{text}{dots}\033[K", end="", flush=True)
            if stop.wait(0.5):
                break

    # Define a daemon thread to run the animation in the background
    thread = threading.Thread(target=animate, daemon=True)
    thread.start()      # Start the animation thread
    try:
        yield
    finally:
        # Runs on success, error and Ctrl-C, so the loading line never stays behind
        stop.set()
        thread.join()
        print("\r\033[K", end="", flush=True)


def main(agent=None, input_fn=input) -> None:
    if agent is None:
        load_dotenv()
        # Verify that API key is set before building the agent
        if not os.getenv("GEMINI_API_KEY"):
            print("GEMINI_API_KEY is not set. Copy .env.example to .env and set your API key.")
            return
        agent = build_agent()
    print("Paste a function or a file path that contains function definition, "
          "then type /send. Commands: /reset, /quit.")
    messages = []
    # Groups this conversation's turns into one LangSmith thread
    thread_id = str(uuid.uuid4())

    # Read user input in a loop, until /quit is typed
    try:
        while True:
            text = read_message(input_fn)
            if text == "/quit":
                break
            if text == "/reset":
                messages = []
                thread_id = str(uuid.uuid4())  # a reset starts a new conversation
                print("Conversation reset.")
                continue
            if not text.strip():
                continue
            
            # Call agent with the accumulated messages and the new user input
            try:
                with loading():
                    response = agent.invoke(
                        {"messages": messages + [HumanMessage(content=text)]},
                        config={"metadata": {"thread_id": thread_id}},
                    )
            except Exception as e:  # noqa: BLE001
                # Keep the session alive on any API or network error, the failed turn is dropped
                print(f"Error invoking agent: {e}")
                continue
                
            messages = response["messages"]
            print(messages[-1].text)
    except KeyboardInterrupt:
        print()
        

if __name__ == "__main__":
    main()
