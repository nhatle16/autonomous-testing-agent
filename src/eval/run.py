import json
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from src.agent import build_agent, build_model
from src.eval.cases import CASES
from src.eval.scores import (
    called_tool_first,
    format_ok,
    functions_covered,
    hit_call_limit,
    parses,
    tool_error_handled,
)

RUNS = 3
MAX_ATTEMPTS = 3  # tries per run in _invoke, so an outage doesn't count as a failure
SCORES = [
    "called_tool_first", "parses", "format_ok", "functions_covered", "tool_error_handled"
]


def _score(case, messages, seconds):
    ai = [m for m in messages if isinstance(m, AIMessage)]
    scored = not case["expect_error"]
    limit = hit_call_limit(messages)
    return {
        "case": case["id"],
        "type": case["type"],
        "model": messages[-1].response_metadata.get("model_name"),
        "called_tool_first": called_tool_first(messages),
        "parses": parses(messages) if scored else None,
        "format_ok": format_ok(messages) if scored else None,
        "functions_covered": functions_covered(messages, case["functions"]) if scored else None,
        # The mirror of parses and format_ok: scored only on error cases
        "tool_error_handled": tool_error_handled(messages) if not scored else None,
        "hit_call_limit": limit,
        "seconds": round(seconds, 2),
        "model_calls": len(ai) - limit,  # the limit message isn't a model call
        "tokens": sum(m.usage_metadata["total_tokens"] for m in ai if m.usage_metadata),
        "reply": messages[-1].text
    }


def _invoke(agent, message):
    """Run one case, trying up to MAX_ATTEMPTS times. Returns (messages, attempts used)."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            result = agent.invoke({"messages": [HumanMessage(content=message)]})
            return result["messages"], attempt + 1
        except Exception:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(5 * (attempt + 1))       # set wait time before retry


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


def main(agent=None):
    """Run every case RUNS times, save each row as a JSON line, then print the summary."""
    if agent is None:
        load_dotenv()
        if not os.getenv("GEMINI_API_KEY"):
            print("GEMINI_API_KEY is not set. Copy .env.example to .env and set your API key.")
            return

        # Use only one known model for every run
        agent = build_agent(model=build_model())

    # Define the output file path
    out = Path("evals/results") / f"{datetime.now():%Y-%m-%d_%H%M}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    with out.open("w") as f:
        for case in CASES:
            for run in range(RUNS):
                print(f"{case['id']} {run + 1}/{RUNS}")
                start = time.perf_counter()
                try:
                    messages, attempts = _invoke(agent, case["message"])
                    row = _score(case, messages, time.perf_counter() - start)
                    # attempts > 1 means part of "seconds" was spent on failed tries
                    row["attempts"] = attempts
                except Exception as e:  # noqa: BLE001
                    # An outage after all retries is recorded, not counted as an agent failure
                    row = {"case": case["id"], "type": case["type"], "error": str(e),
                           "attempts": MAX_ATTEMPTS}

                # Which of the RUNS repeats this row is
                row["run"] = run

                # Write each row right away, so a crash keeps the finished runs
                f.write(json.dumps(row) + "\n")
                f.flush()
                rows.append(row)

    _summary(rows)
    print(f"Results: {out}")


if __name__ == "__main__":
    main()
