import ast
import re

from langchain_core.messages import AIMessage, HumanMessage


def _reply(messages):
    """Return the text of the last message, which is the agent's final reply."""
    # .text, not .content: Gemini can return content as a list of parts
    return messages[-1].text


def _extract_python_blocks(text):
    """Return the code inside each ```python block of text."""
    return re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)


def parses(messages):
    """True if the reply's first python block is valid Python. It is parsed, never run."""
    blocks = _extract_python_blocks(_reply(messages))
    if not blocks:
        return False
    try:
        ast.parse(blocks[0])
    # ValueError: Python 3.11 raises it for null bytes instead of SyntaxError
    except (SyntaxError, ValueError):
        return False
    return True


def format_ok(messages):
    """True if the reply has exactly one fenced block, a python one, then an "Assumptions" list."""
    text = _reply(messages)
    return (
        len(_extract_python_blocks(text)) == 1
        and text.count("```") == 2  # no second fence of another language
        # rfind: the word may also appear inside the code, e.g. in a comment
        and text.rfind("Assumptions") > text.rfind("```")
    )


def called_tool_first(messages):
    """True if the first AI message of the latest turn calls read_input."""
    # The latest turn starts at the last HumanMessage; the chat keeps earlier turns
    start = 0
    for i, m in enumerate(messages):
        if isinstance(m, HumanMessage):
            start = i

    for m in messages[start:]:
        if isinstance(m, AIMessage):
            return bool(m.tool_calls) and m.tool_calls[0]["name"] == "read_input"
    return False


def hit_call_limit(messages):
    """True if ModelCallLimitMiddleware stopped the run before the agent replied."""
    # The middleware ends the run with this message without calling the model
    return _reply(messages).startswith("Model call limits exceeded")


def tool_error_handled(messages):
    """True if the reply explains the error and drafts no tests, as the prompt requires."""
    text = _reply(messages)
    # A fixed version of the code is a fair suggestion; only drafted tests count as a failure
    return bool(text.strip()) and "def test_" not in text and not hit_call_limit(messages)
