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
        except Exception:
            if attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))       # set wait time before retry


SCORES = ["called_tool_first", "parses", "format_ok"]


def _mean(rows, key):
    """Average of key over the rows that have it; None when no row does."""
    vals = [r[key] for r in rows if r.get(key) is not None]
    return sum(vals) / len(vals) if vals else None


def _fmt(value, spec):
    return "-" if value is None else format(value, spec)


def _summary(rows):
    """Print pass rates, errors, time and tokens per case type, then for all cases."""
    by_type = defaultdict(list)
    for r in rows:
        by_type[r["type"]].append(r)
    by_type["all"] = rows

    print(f"{'type':<18}{'runs':>5}{'errors':>7}"
        + "".join(f"{s:>19}" for s in SCORES) + f"{'secs':>7}{'tokens':>8}")

    for type_, group in by_type.items():
        errors = sum("error" in r for r in group)
        print(f"{type_:<18}{len(group):>5}{errors:>7}"
                + "".join(f"{_fmt(_mean(group, s), '.0%'):>19}" for s in SCORES)
                + f"{_fmt(_mean(group, 'seconds'), '.1f'):>7}"
                + f"{_fmt(_mean(group, 'tokens'), '.0f'):>8}")
