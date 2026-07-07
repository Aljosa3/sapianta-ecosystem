# G15-AICLI-07 - Terminal Rendering Lifecycle Audit

Status: AUDIT COMPLETE
Date: 2026-07-07
Scope: AiCLI terminal rendering during clarification compose mode.

## Executive Summary

The observed behavior is caused by clarification compose prompt rendering inside a line-by-line `input()` loop.

G15-HIR-05 correctly introduced a clarification compose buffer, but the compose reader renders:

`aicli clarification compose>`

before every subsequent physical terminal read while the buffer is non-empty. In a real terminal, a large paste is commonly delivered to Python `input()` one completed line at a time. Between those reads, AiCLI prints the compose prompt again. The terminal may still be echoing or processing the pasted content, so the prompt appears inside the user's pasted text.

This is a Human Interface terminal rendering lifecycle defect. It is not a Platform Core clarification semantics defect.

No production code was modified in this audit.

Final classification:

AICLI_CLARIFICATION_COMPOSE_PROMPT_RENDERING_REPEATS_DURING_PASTE

## Knowledge Reuse Audit

Existing relevant implementation:

- `run_reference_uhi_submit_session()`
  - owns submit-mode terminal session lifecycle.
  - calls `_read_clarification_reply()` while Platform Core is waiting for clarification.
- `_read_clarification_reply()`
  - owns clarification compose input capture.
  - stores physical lines in `reply_buffer`.
  - submits only on `/send` or `.`.
  - calls `_split_input_chunk()` for a returned input chunk.
- `_split_input_chunk()`
  - handles the case where an input reader returns a multi-line chunk in one call.
  - suppresses repeated prompt rendering only for lines already stored in `pending_lines`.
- `_submit_composed_request()`
  - remains the single Platform Core submission path.
- `tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py`
  - proves multi-line replies work when the test input reader returns the whole paste as one string.

No existing production code distinguishes real terminal line-by-line paste from a test reader returning a whole multi-line chunk.

## Runtime Trace

Current clarification compose lifecycle:

1. Platform Core asks a clarification question.
2. AiCLI enters `_read_clarification_reply()`.
3. `reply_buffer` is empty.
4. AiCLI calls `input_reader("aicli clarification> ")`.
5. The terminal returns one line.
6. AiCLI appends that line to `reply_buffer`.
7. `pending_lines` is empty.
8. AiCLI loops.
9. Because `reply_buffer` is non-empty, AiCLI calls `input_reader("aicli clarification compose> ")`.
10. The prompt is rendered before the next terminal line is read.
11. During a paste, this can repeat for every physical line.
12. If `/send` is read as a clean standalone line, compose mode terminates.
13. If terminal echo and prompt rendering make the displayed paste ambiguous, the user may perceive `/send` as not reliably transitioning.

Implementation evidence:

- `aicli.py` lines 369-372 enter `_read_clarification_reply()` while pending clarification exists.
- `aicli.py` lines 547-584 implement the clarification compose loop.
- `aicli.py` lines 560-562 render either `aicli clarification>` or `aicli clarification compose>` on every blocking read.
- `aicli.py` lines 565-568 avoid additional prompts only for extra lines already returned inside the same input chunk.
- `aicli.py` lines 580-583 terminate compose mode only when `/send` or `.` reaches the loop as a normalized standalone line.

## Root Cause Analysis

The cause is repeated prompt rendering.

The problem is not:

- Platform Core clarification continuity.
- Human Intent Resolution.
- governance.
- replay.
- provider or worker behavior.
- stdout/stderr interleaving.

The problem is also not multiple Platform Core input loops. The outer submit loop calls `_read_clarification_reply()` once per logical reply. The repeated rendering occurs inside `_read_clarification_reply()` before each physical line read.

The pending input buffer works only when one `input_reader()` call returns a multi-line string. That is what current regression tests simulate. A real terminal `input()` call normally returns one line at a time, so `pending_lines` is empty after each physical line, and the next loop iteration prints another prompt.

`/send` detection is deterministic in code. It works if the line received by `input()` normalizes exactly to `/send` or `.`. The real-world failure is that terminal rendering makes the paste lifecycle visually unstable, and the prompt can be interleaved with pasted text before `/send` is read.

## Ownership Analysis

AiCLI owns:

- terminal input capture.
- local compose buffering.
- local command delimiters such as `/send`, `.`, `/cancel`, and `/exit`.
- prompt rendering.

Platform Core owns:

- clarification semantics.
- Human Intent Resolution.
- Knowledge Reuse.
- governance.
- replay.
- runtime orchestration.
- provider and worker boundaries.

Therefore the correction belongs in AiCLI, but only in terminal input rendering/capture. AiCLI must not decide clarification sufficiency or inspect semantic content.

## Minimal Fix Recommendation

Smallest architecture-safe correction:

Render the clarification compose instruction once, then read subsequent physical lines with an empty prompt until `/send`, `.`, `/cancel`, `/exit`, or EOF.

Recommended behavior:

1. When clarification input begins, render one visible prompt/instruction.
2. After the first line is buffered, do not render `aicli clarification compose>` before every additional physical read.
3. Continue collecting lines until `/send` or `.`.
4. Preserve internal line breaks.
5. Submit the aggregated reply exactly once to `_submit_composed_request()`.

This keeps all semantic ownership in Platform Core and changes only terminal rendering lifecycle.

Potential implementation shape:

- Change `_read_clarification_reply()` so its first `input_reader()` call uses `aicli clarification> `.
- Subsequent reads use `input_reader("")` or another no-visible-prompt mechanism while the buffer is non-empty.
- Keep `/send`, `.`, `/cancel`, `/exit`, EOF, and empty input behavior unchanged.
- Add a regression test with a prompt-recording reader that returns one physical line per call and verifies the compose prompt is not repeatedly rendered for each line.

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/cli/aicli.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- `python -m py_compile aigol/cli/aicli.py` passed.
- `python -m pytest -q` passed: `5821 passed, 4 skipped`.
- `git diff --check` passed.

## Files Modified

- `docs/governance/G15_AICLI_07_TERMINAL_RENDERING_LIFECYCLE_AUDIT.md`

## Boundary Confirmation

No production runtime behavior was changed by this audit.

No Platform Core responsibility moved into AiCLI.

No governance, replay, provider, worker, or runtime orchestration behavior was changed.

The recommended correction is Human Interface input rendering only.

## Final Determination

AiCLI renders clarification prompts inside pasted text because `_read_clarification_reply()` prints a compose prompt before every blocking physical line read after the buffer is non-empty.

The smallest safe correction is to render the clarification prompt once and continue reading buffered physical lines without repeated visible prompt output until the user sends `/send` or `.`.
