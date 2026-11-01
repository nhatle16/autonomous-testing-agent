# Graph Report - autonomous-testing-agent  (2026-11-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 100 nodes · 162 edges · 10 communities (6 shown, 4 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0b1619e5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7

## God Nodes (most connected - your core abstractions)
1. `_inputs()` - 12 edges
2. `main()` - 11 edges
3. `read_message()` - 9 edges
4. `FakeAgent` - 8 edges
5. `loading()` - 8 edges
6. `read_input()` - 7 edges
7. `build_agent()` - 7 edges
8. `_describe_function()` - 6 edges
9. `_param()` - 6 edges
10. `_message_counts()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `test_loading_animates_and_clears_in_terminal()` --calls--> `loading()`  [EXTRACTED]
  tests/test_chat.py → src/chat.py
- `test_loading_prints_nothing_outside_terminal()` --calls--> `loading()`  [EXTRACTED]
  tests/test_chat.py → src/chat.py
- `test_main_keeps_history_across_turns()` --calls--> `main()`  [EXTRACTED]
  tests/test_chat.py → src/chat.py
- `test_main_keeps_running_after_agent_error()` --calls--> `main()`  [EXTRACTED]
  tests/test_chat.py → src/chat.py
- `test_main_quits_on_eof()` --calls--> `main()`  [EXTRACTED]
  tests/test_chat.py → src/chat.py

## Import Cycles
- None detected.

## Communities (10 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.24
Nodes (15): main(), read_message(), FakeAgent, _inputs(), _message_counts(), test_main_keeps_history_across_turns(), test_main_keeps_running_after_agent_error(), test_main_quits_on_eof() (+7 more)

### Community 1 - "Community 1"
Cohesion: 0.15
Nodes (5): _describe_function(), _describe_parameters(), _param(), read_input(), read_source_code()

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (9): _names(), _param(), test_read_input_aligns_defaults_with_last_positional_parameters(), test_read_input_describes_every_parameter_kind(), test_read_input_includes_async_functions(), test_read_input_keeps_source_order(), test_read_input_reads_sample_file(), test_read_input_returns_error_when_no_top_level_function() (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (4): build_model(), loading(), test_loading_animates_and_clears_in_terminal(), test_loading_prints_nothing_outside_terminal()

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (4): build_agent(), _fake_model(), FakeToolModel, test_agent_calls_read_input_then_replies_with_tests()

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (4): add(), divide(), multiply(), substract()

## Knowledge Gaps
- **1 isolated node(s):** `autonomous-testing-agent`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 43 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `read_input()` connect `Community 1` to `Community 2`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **What connects `autonomous-testing-agent` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Why does `build_agent()` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.14705882352941177 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `Community 0` to `Community 3`, `Community 4`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._