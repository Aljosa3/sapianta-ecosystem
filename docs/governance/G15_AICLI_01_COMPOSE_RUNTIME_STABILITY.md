# G15_AICLI_01_COMPOSE_RUNTIME_STABILITY

Final verdict: AICLI_COMPOSE_RUNTIME_STABILITY_CERTIFIED

## Objective

Stabilize the reference AiCLI compose runtime so large pasted Generation 15 development prompts can be accepted without prompt flooding, repeated rendering, or input loss.

This milestone is limited to the Human Interface adapter input loop.

## Root Cause

`run_reference_uhi_session()` previously called:

```text
input_reader("aicli compose> " if compose_buffer else "aicli> ")
```

for every physical line consumed by the terminal.

For short interactive compose sessions this was correct.

For a large pasted multi-line prompt, terminal buffering can make AiCLI consume many lines in rapid succession. Because the prompt was rendered for every consumed line, the terminal appeared to flood with:

```text
aicli compose>
aicli compose>
aicli compose>
```

The defect was adapter-local prompt rendering and buffering behavior. It was not a Platform Core, conversation ownership, runtime entry, provider, worker, or replay defect.

## Fix

AiCLI now keeps an internal pending input line buffer.

When `input_reader(...)` returns a chunk containing newlines, AiCLI splits the chunk once and processes the buffered lines without re-rendering a terminal prompt for each internal pasted line.

EOF handling remains fail-safe:

- EOF with a non-empty compose buffer submits the composed request to Platform Core.
- blank top-level pasted lines are ignored without submitting;
- blank lines inside a compose buffer are preserved;
- `/send`, `.`, `/approve`, `/cancel`, and `/exit` semantics are unchanged.

## Boundary Preservation

Preserved:

- Platform Core owns project services, conversation, and semantic interpretation.
- Human Interface remains a thin adapter.
- Provider Platform remains unchanged.
- Runtime Entry remains unchanged.
- Replay remains unchanged.

No Platform Core behavior was moved into AiCLI.

## Regression Coverage

Added:

```text
tests/test_g15_aicli_01_compose_runtime_stability.py
```

Coverage includes:

- short compose sessions still work;
- large pasted prompts are processed from one input cycle;
- prompt rendering does not flood for buffered paste chunks;
- blank lines inside pasted prompts are preserved;
- EOF after a non-empty compose buffer submits safely;
- blank top-level paste content is ignored safely.

Focused validation:

```text
python -m pytest -q tests/test_g15_aicli_01_compose_runtime_stability.py tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_47_human_intent_to_capability_resolution_v1.py tests/test_g14_48_goal_oriented_clarification_experience_v1.py
21 passed
```

Full repository validation is recorded in the implementation response.

## Certification

AiCLI compose runtime is stable for large pasted Generation 15 prompts while preserving certified Generation 14 ownership boundaries.
