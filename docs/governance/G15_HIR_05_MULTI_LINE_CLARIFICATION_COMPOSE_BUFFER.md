# G15-HIR-05 - Multi-Line Clarification Compose Buffer

Status: IMPLEMENTED
Date: 2026-07-07
Scope: AiCLI clarification input capture for persistent submit sessions.

## Executive Summary

G15-HIR-05 implements the smallest correction recommended by G15-HIR-04:

AICLI_CLARIFICATION_REPLY_INPUT_AGGREGATION_MISSING

Clarification follow-up input in `./aicli submit` now uses a compose buffer. Physical terminal lines are collected until the human enters `/send` or a single `.` line. AiCLI then forwards exactly one clarification reply to Platform Core through the existing project-context submission path.

Platform Core clarification semantics remain unchanged.

## Knowledge Reuse Audit

Existing reusable implementation was retained:

- `AICLI_SEND_COMMANDS`
  - reused for `/send` and `.` submission delimiters.
- `_split_input_chunk()`
  - reused so pasted multi-line input can be processed deterministically without repeated prompt flooding.
- `_submit_composed_request()`
  - remains the single path for forwarding user text to Platform Core project services.
- `_normalize_submit_request()`
  - initial submit behavior remains unchanged.
- Platform Core project services
  - remain the owner of clarification continuity, intent resolution, approval summaries, and replay-backed workspace state.

No clarification sufficiency rules were added to AiCLI.

## Architectural Review

This milestone changes only terminal input aggregation.

AiCLI owns:

- terminal input capture.
- local compose buffering.
- rendering the `/send` / `.` instruction.
- forwarding one intended reply to Platform Core.

Platform Core owns:

- clarification semantics.
- Human Intent Resolution.
- Knowledge Reuse.
- replay-backed clarification continuity.
- approval summary creation.
- governance and runtime orchestration.

No governance, replay, provider, worker, or semantic authority moved into AiCLI.

## Implementation Summary

Implemented:

- `_read_clarification_reply()`
  - reads clarification input into a local buffer.
  - supports pasted multi-line chunks.
  - preserves internal line breaks.
  - submits only on `/send` or `.`.
  - supports `/cancel`, `/exit`, EOF, and empty input safely.
- `run_reference_uhi_submit_session()`
  - now calls `_read_clarification_reply()` when Platform Core is waiting for clarification.
  - forwards the composed reply as split lines to `_submit_composed_request()`, preserving the existing compose behavior and multiline counters.
- `_render_clarification()`
  - now tells the user to finish clarification replies with `/send` or `.`.

Unchanged:

- initial submit mode still uses `sys.stdin.read()`.
- approval mode remains single-command input.
- Platform Core project services remain authoritative for semantic decisions.
- runtime approval delegation is unchanged.

## Regression Tests

Added:

- `tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py`

Coverage proves:

- a multi-line clarification reply pasted as one chunk is submitted once.
- internal line breaks are preserved in Platform Core `raw_prompt`.
- only two UHI project-context artifacts are produced: the original request and the aggregated clarification reply.
- the runtime receives the full clarification reply, not the last physical line.
- cancellation while composing a clarification reply discards the buffer and does not submit a partial reply.
- AiCLI remains non-authoritative.

Updated existing tests:

- `tests/test_g15_aicli_03_persistent_platform_conversation_session.py`
- `tests/test_g15_hir_02_replay_backed_clarification_continuity.py`

The updates add explicit `/send` delimiters for clarification replies, matching the new compose-mode contract.

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/cli/aicli.py`
- `python -m pytest -q tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g15_hir_02_replay_backed_clarification_continuity.py tests/test_g15_aicli_02_submission_mode.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- Focused validation passed: `14 passed`.
- Full repository validation passed: `5821 passed, 4 skipped`.
- Diff whitespace validation passed.

## Files Modified

- `aigol/cli/aicli.py`
- `tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py`
- `tests/test_g15_aicli_03_persistent_platform_conversation_session.py`
- `tests/test_g15_hir_02_replay_backed_clarification_continuity.py`
- `docs/governance/G15_HIR_05_MULTI_LINE_CLARIFICATION_COMPOSE_BUFFER.md`

## Boundary Confirmation

AiCLI aggregates physical terminal lines into one user reply.

AiCLI does not:

- decide whether clarification is resolved.
- inspect the semantic content of the reply.
- create approval.
- authorize governance.
- invoke providers.
- invoke workers.
- own replay.

Platform Core receives one intended clarification reply and remains responsible for all interpretation and governed continuation.

## Final Determination

Multi-line clarification reply capture is implemented.

The human can now paste or type multiple clarification lines, finish with `/send` or `.`, and AiCLI forwards exactly one clarification message to Platform Core with internal line breaks preserved.
