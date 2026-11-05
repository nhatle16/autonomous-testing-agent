import re


def _reply(messages):
    """Helper: return the text of the last AIMessage in messages."""
    return messages[-1].text


def _extract_python_blocks(text):
    """Helper: extract Python code blocks from the reply."""
    return re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
