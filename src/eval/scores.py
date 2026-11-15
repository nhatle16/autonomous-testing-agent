import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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


def functions_covered(messages, functions):
    """True if the reply has a test_<name> test for every function in functions."""
    text = _reply(messages)
    # shortcut: matches by test name only, so test_div_zero misses divide; use ast if this misleads
    return all(re.search(rf"def test_{re.escape(name)}(_|\()", text) for name in functions)


def tests_pass(messages, message):
    """True if the reply's python block passes pytest against the case's code. Runs in a temp folder."""
    # Get the Python code block
    blocks = _extract_python_blocks(_reply(messages))
    if not blocks:
        return False
    
    # Create a temprorary directory to run pytest
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "test_draft.py").write_text(blocks[0])       # get the draft's tests
        
        if "\n\n" in message:
            # Split at the first blank line to get the function in the prompt
            (tmp / "my_module.py").write_text(message.split("\n\n", 1)[1])
        
        # The draft is model-written code, so it must not see the API key
        env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
        env["PYTHONPATH"] = os.getcwd()  # so file cases can import src.samples.sample2

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q"],
                check=False, cwd=tmp, env=env, capture_output=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            return False
        return result.returncode == 0
