from langchain_core.messages import AIMessage

# Imported as a module: a bare tests_pass name would be collected by pytest as a test
from src.eval import scores

SQUARE_MESSAGE = "Write pytest tests for this function:\n\ndef square(x):\n    return x * x\n"


def _reply(code):
    """An agent reply holding code in one python block."""
    return [AIMessage(f"```python\n{code}```\n\nAssumptions:\n- none")]


def test_tests_pass_true_when_draft_passes():
    draft = "from my_module import square\n\ndef test_square():\n    assert square(3) == 9\n"
    assert scores.tests_pass(_reply(draft), SQUARE_MESSAGE) is True


def test_tests_pass_false_when_draft_fails():
    draft = "from my_module import square\n\ndef test_square():\n    assert square(3) == 10\n"
    assert scores.tests_pass(_reply(draft), SQUARE_MESSAGE) is False


def test_tests_pass_false_without_python_block():
    assert scores.tests_pass([AIMessage("No tests, sorry.")], SQUARE_MESSAGE) is False


def test_tests_pass_imports_file_cases_from_the_repo():
    draft = "from src.samples.sample2 import divide\n\ndef test_divide():\n    assert divide(6, 3) == 2\n"
    assert scores.tests_pass(_reply(draft), "Write pytest tests for src/samples/sample2.py") is True


def test_tests_pass_hides_the_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "dummy")
    draft = "import os\n\ndef test_no_key():\n    assert 'GEMINI_API_KEY' not in os.environ\n"
    assert scores.tests_pass(_reply(draft), SQUARE_MESSAGE) is True
