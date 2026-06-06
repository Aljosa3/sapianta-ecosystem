# AIGOL_REPL_REENTRY_BUFFER_ELIMINATION_V1

## Status

Runtime fix and replay-safe regression certification.

Interactive REPL behavior is preserved. Multiline prompt support is preserved. Replay compatibility is preserved. Fail-closed behavior is preserved.

## Executive Finding

The phantom second turn was caused by premature multiline capture termination before the sentinel was consumed.

The responsible location was:

```text
aigol/cli/aigol_cli.py::_read_interactive_prompt_capture
```

Before the fix, the function entered multiline mode after detecting buffered input, but then rechecked `_has_buffered_multiline_input(...)` after each continuation line. If that readiness check returned `False` before the `.` sentinel was read, capture ended early and left the sentinel or following residual input in stdin.

The next `run_interactive_conversation(...)` loop iteration then consumed that residual line as a new prompt. For an unmatched residual prompt, routing selected:

```text
DEFAULT_PROVIDER_ASSISTED_CONVERSATION
```

which could then fail closed through the provider-assisted fallback path.

## Direct Answers

1. Stdin buffering could remain after multiline capture because capture could stop before reading the sentinel.

2. The multiline sentinel could remain as residual input when the post-continuation readiness check returned false before the sentinel was consumed.

3. REPL reentry consumed residual input at the next top-level prompt read in `run_interactive_conversation(...)`.

4. The exact responsible location was the inner multiline loop in `_read_interactive_prompt_capture(...)`.

## Root Cause

The old capture shape was:

```text
raw_prompt = input_reader("AiGOL > ")
if no buffered input:
    return single-line prompt

while True:
    continuation = input_reader("... ")
    if continuation == ".":
        break
    lines.append(continuation)
    if no buffered input:
        break
```

That final readiness-based break was not a constitutional turn boundary. It was a terminal buffering observation. Treating it as authoritative allowed a transient buffering gap to end the governed turn before the declared sentinel.

## Fix

Once multiline mode starts, `_read_interactive_prompt_capture(...)` now reads until:

- the configured sentinel `.` is consumed;
- or EOF is encountered.

It no longer exits multiline capture because `_has_buffered_multiline_input(...)` temporarily reports no pending input after a continuation line.

The sentinel is consumed and excluded from the assembled prompt. It cannot be consumed by REPL reentry as a separate prompt.

## Preservation Guarantees

- Single-line prompts still use the existing `AiGOL > ` prompt and exit command behavior.
- Multiline pasted prompts still use the `.` sentinel and record `MULTILINE_PROMPT_CAPTURED_ARTIFACT_V1`.
- Replay artifacts still declare `terminator_included: False`, `single_turn_guarantee: True`, and `fragment_turns_created: False`.
- Fail-closed runtime branches were not weakened or bypassed.
- No provider, workflow, or dispatch authority was added.

## Acceptance Evidence

Regression coverage was added in:

```text
tests/test_multiline_prompt_support_runtime_v1.py::test_multiline_reentry_does_not_consume_sentinel_as_second_turn
```

The regression simulates a buffered multiline paste where `has_pending_input()` returns:

```text
[True, False]
```

before the sentinel is read. The certified result is:

```text
turn_count = 1
failed_turns = 0
TURN-* directories = 1
terminator_included = False
single_turn_guarantee = True
fragment_turns_created = False
```

## Validation

```bash
python -m pytest tests/test_multiline_prompt_support_runtime_v1.py
python -m pytest tests/test_interactive_conversation_cli_v1.py
```

Both focused suites passed.

## Final Outputs

```text
PHANTOM_SECOND_TURN_ELIMINATED = TRUE
ROOT_CAUSE = premature multiline capture termination left sentinel/residual stdin for REPL reentry
FIX_REQUIRED = TRUE_APPLIED
```
