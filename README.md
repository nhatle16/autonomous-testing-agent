# autonomous-testing-agent

A command-line chat agent that drafts pytest tests for your Python functions. Paste a function, or
give a path to a `.py` file, and the agent replies with a test file plus a list of the assumptions
it made.

It is built with LangChain and Google Gemini. The agent reads your code with Python's `ast`
module, so your code is parsed but never executed.

## How it works

1. You send a message with code or a file path.
2. The agent calls its `read_input` tool, which parses the code and extracts each top-level
   function: name, docstring, parameters, annotations, defaults, return type and source.
3. Gemini writes the tests from that description and replies with one ```` ```python ```` block
   and an "Assumptions" list.

## Setup

Requires Python 3.11 or newer and a [Gemini API key](https://aistudio.google.com/apikey).

```bash
python -m venv .venv
source .venv/bin/activate
pip install langchain langchain-google-genai python-dotenv pytest ruff
cp .env.example .env
```

Then edit `.env`:

| Variable | Required | Default |
|---|---|---|
| `GEMINI_API_KEY` | yes | — |
| `GEMINI_MODEL` | no | `gemini-3.1-flash-lite` |
| `GEMINI_MAX_OUTPUT_TOKENS` | no | `2048` |
| `LANGSMITH_TRACING` | no | `false` |
| `LANGSMITH_API_KEY` | only for tracing | — |
| `LANGSMITH_PROJECT` | no | `default` |

### Tracing (optional)

To see every step the agent takes, set `LANGSMITH_TRACING=true` and add a
[LangSmith](https://smith.langchain.com) API key. Each chat turn then appears in the LangSmith
project as a trace: the model call, the `read_input` tool call and the final reply, with inputs,
outputs, token counts and timings. No code change is needed.

Traces include the code you send, and they are stored on LangSmith's servers. Leave tracing off
for code you can't share.

## Usage

Start the chat from the repo root:

```bash
python -m src.chat
```

Type or paste your message over as many lines as you like, then type `/send` on its own line.

| Command | What it does |
|---|---|
| `/send` | Send the message typed so far |
| `/reset` | Clear the conversation history (first line only) |
| `/quit` | Exit (first line only); Ctrl-D and Ctrl-C also exit |

Example session (illustrative and shortened; real replies vary):

````text
Write tests for divide in src/samples/sample2.py
/send

```python
import pytest

from src.samples.sample2 import divide


def test_divide_returns_quotient():
    assert divide(6, 3) == 2


def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError):
        divide(1, 0)
```

Assumptions:
- ...
````

The agent remembers the conversation, so you can follow up, for example "add a test for negative
numbers", without pasting the code again.

For a single run without the chat, `python -m src.agent` drafts tests for `divide` in
`src/samples/sample2.py` and prints the reply.

## Limitations

- **Drafts only.** The agent never writes test files or runs tests. Review the draft, save it
  yourself, and run it with pytest.
- **Top-level functions only.** Class methods and nested functions are skipped.
- **Based on the source.** The tests reflect what the code and docstring say, so a bug in the code
  can end up in the expected values. Check the "Assumptions" list.

## Development

```bash
pytest           # run the test suite (no API key or network needed)
ruff check .     # lint
```

Tests replace Gemini with scripted fake models and fake agents, so they never call the API.

## Project layout

```text
src/
  agent.py              # system prompt, build_model(), build_agent()
  chat.py               # interactive chat loop
  tools/read_source.py  # read_input tool: parses code with ast
  samples/              # example input files
tests/                  # pytest suite
```
