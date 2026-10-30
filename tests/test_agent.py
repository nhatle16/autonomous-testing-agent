from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from src.agent import SYSTEM_PROMPT, build_agent

TEST_DRAFT = """\
```python
from src.samples.sample2 import divide

def test_divide_returns_quotient():
    assert divide(6, 3) == 2
```
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


def test_agent_calls_read_input_then_replies_with_tests():
    agent = build_agent(model=_fake_model())
    
    result = agent.invoke(
        {"messages": [HumanMessage(content="Write tests for divide in src/samples/sample2.py")]}
    )
    
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].name == "read_input"
    assert "divide" in tool_messages[0].text
    assert "def test_" in result["messages"][-1].text


def test_system_prompt_requires_read_input_first():
    assert "call the `read_input` tool first" in SYSTEM_PROMPT
