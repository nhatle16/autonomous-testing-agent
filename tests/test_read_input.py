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


def _names(result):
    return [function["name"] for function in result]


def test_read_input_skips_nested_functions():
    source = "def outer():\n    def inner():\n        pass\n"

    assert _names(read_input.invoke({"text": source})) == ["outer"]


def test_read_input_includes_async_functions():
    source = "async def fetch():\n    pass\n"

    assert _names(read_input.invoke({"text": source})) == ["fetch"]


def test_read_input_keeps_source_order():
    source = "def b():\n    pass\n\ndef a():\n    pass\n"

    assert _names(read_input.invoke({"text": source})) == ["b", "a"]


@pytest.mark.parametrize(
    "source",
    [
        "x = 1\n",
        "",
        "class A:\n    def method(self):\n        pass\n",
    ],
    ids=["statement-only", "empty", "method-only"],
)
def test_read_input_returns_error_when_no_top_level_function(source):
    assert read_input.invoke({"text": source}) == {"error": "No top-level function found"}


def test_read_input_reads_sample_file():
    result = read_input.invoke({"path": "src/samples/sample2.py"})

    assert _names(result) == ["add", "substract", "multiply", "divide"]
