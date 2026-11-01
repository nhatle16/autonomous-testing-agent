import os

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


def main(agent=None, input_fn=input) -> None:
    if agent is None:
        load_dotenv()
        # Verify that API key is set before building the agent
        if not os.getenv("GEMINI_API_KEY"):
            print("GEMINI_API_KEY is not set. Copy .env.example to .env and set your API key.")
            return
        agent = build_agent()
    print("Paste a function or a file path that contains function definition,"
          "then type /send. Commands: /reset, /quit.")
    messages = []
    
    # Read user input in a loop, until /quit is typed
    try:
        while True:
            text = read_message(input_fn)
            if text == "/quit":
                break
            if text == "/reset":
                messages = []
                print("Conversation reset.")
                continue
            if not text.strip():
                continue
            
            # Call agent with the accumulated messages and the new user input
            try:
                response = agent.invoke(
                    {"messages": messages + [HumanMessage(content=text)]}
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
