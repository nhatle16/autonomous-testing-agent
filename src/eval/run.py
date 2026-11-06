import time
from collections import defaultdict

from langchain_core.messages import AIMessage, HumanMessage

from src.eval.scores import called_tool_first, format_ok, parses


def _score(case, messages, seconds):
    ai = [m for m in messages if isinstance(m, AIMessage)]
    scored = not case["expect_error"]
    return {
        "case": case["id"],
        "type": case["type"],
        "model": messages[-1].response_metadata.get("model_name"),
        "called_tool_first": called_tool_first(messages),
        "parses": parses(messages) if scored else None,
        "format_ok": format_ok(messages) if scored else None,
        "seconds": round(seconds, 2),
        "model_calls": len(ai),
        "tokens": sum(m.usage_metadata["total_tokens"] for m in ai if m.usage_metadata),
        "reply": messages[-1].text
    }


def _invoke(agent, message):
    """Proceed one run with maximum 3 retries"""
    for attempt in range(3):
        try:
            return agent.invoke({"messages": [HumanMessage(content=message)]})["messages"]
        except Exception:   # noqa: BLE001
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))       # set wait time before retry
