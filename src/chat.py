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
    