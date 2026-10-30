from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

TEST_DRAFT = """\
```python
from src.samples.sample2 import divide

def test_divide_returns_quotient():
    assert divide(6, 3) == 2
"""


class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


# Return a fake model with scripted messages that call the read_input tool and then return a test draft.
def _fake_model():
    return FakeToolModel(
        messages=iter([
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "read_input",
                        "args": {"path": "src/samples/sample2.py"},
                        "id": "call_1"
                    }
                ]
            ),
            AIMessage(content=TEST_DRAFT)
        ])
    )
