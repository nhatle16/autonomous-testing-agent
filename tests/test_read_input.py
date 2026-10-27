import pytest

from src.tools.read_source import read_input


def test_read_input_parses_source_text():
    source = 'def greet(name):\n    """Say hello."""\n    pass\n'

    assert read_input.invoke({"text": source}) == [
        {"name": "greet", "docstring": "Say hello.", "arguments": ["name"]}
    ]


def test_read_input_reads_source_from_file(tmp_path):
    source_file = tmp_path / "example.py"
    source_file.write_text("def greet():\n    pass\n", encoding="utf-8")

    assert read_input.invoke({"path": str(source_file)}) == [
        {"name": "greet", "docstring": None, "arguments": []}
    ]


def test_read_input_requires_text_or_path():
    with pytest.raises(ValueError, match="Provide code or a file"):
        read_input.invoke({})


def test_read_input_returns_syntax_error_for_invalid_text():
    assert read_input.invoke({"text": "def broken(:"}) == {
        "error": "Source code:1: invalid syntax"
    }
