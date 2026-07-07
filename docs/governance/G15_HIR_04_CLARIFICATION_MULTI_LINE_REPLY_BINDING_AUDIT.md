# G15-HIR-04 - Clarification Multi-Line Reply Binding Audit

Status: AUDIT COMPLETE
Date: 2026-07-07
Scope: Multi-line clarification replies in persistent AiCLI submit sessions.

## Executive Summary

The observed behavior is caused by AiCLI submit-mode continuation input handling.

Initial submit mode correctly accepts a large multi-line request through `sys.stdin.read()` and submits it once. Interactive compose mode also has a compose buffer and `/send` delimiter. However, persistent submit-mode clarification follow-up reads exactly one terminal line with:

`input_reader("aicli clarification> ")`

and immediately submits that single physical line as:

`compose_buffer=[reply_text]`

Therefore, when a human pastes a multi-line clarification reply at the clarification prompt, the terminal/input stack supplies the paste as multiple line reads. AiCLI treats each physical line as a separate clarification answer and sends each to Platform Core as a separate message. Platform Core then receives multiple independent `original_request` values rather than one intended clarification reply.

No production code was changed in this audit.

Final classification:

AICLI_CLARIFICATION_REPLY_INPUT_AGGREGATION_MISSING

## Knowledge Reuse Audit

Existing reusable input handling was found:

- Initial submit mode:
  - `run_reference_uhi_submit_session()` reads the initial request with `sys.stdin.read()`.
  - `_normalize_submit_request()` preserves internal line breaks and strips only outer empty lines.
- Interactive compose mode:
  - uses `compose_buffer`.
  - accepts `/send` or `.` as explicit submit delimiters.
  - uses `_split_input_chunk()` to split pasted chunks deterministically.
  - submits the composed request once through `_submit_composed_request()`.
- Persistent submit-mode clarification:
  - reuses `_submit_composed_request()`.
  - does not reuse compose buffering or EOF-style aggregation.

Existing tests prove the reusable pieces:

- `tests/test_g15_aicli_01_compose_runtime_stability.py` verifies large pasted compose input is submitted once and preserves blank lines.
- `tests/test_g15_aicli_02_submission_mode.py` verifies initial submit mode accepts large multi-line prompts once and preserves internal line breaks.
- `tests/test_g15_aicli_03_persistent_platform_conversation_session.py` verifies persistent clarification sessions work for single-line clarification replies.

No existing test currently proves multi-line clarification replies are aggregated as one reply.

## Root Cause Analysis

The root cause is not Platform Core clarification continuity.

Platform Core can only bind the message it receives. In the observed failure, AiCLI sends separate messages:

- `The next change is ...`
- `The Governed Development Execution Bridge ...`
- `The purpose of this audit ...`
- `No Human Interface behaviour shall change.`

Each message is independently submitted to Platform Core via `_submit_composed_request()`, so each becomes an independent `original_request`.

Implementation evidence:

- `aicli.py` lines 295-299 read the initial submit request using stdin read semantics.
- `aicli.py` lines 324-332 submit the initial multi-line request once by splitting it into a compose buffer.
- `aicli.py` lines 369-376 read a clarification reply with one `input_reader("aicli clarification> ")` call.
- `aicli.py` lines 391-406 immediately submit that one reply as `compose_buffer=[reply_text]`.
- `aicli.py` lines 617-625 provide `_split_input_chunk()`, but that helper is used by interactive compose mode, not the submit-mode clarification follow-up path.

The deterministic mechanism is:

1. Pending clarification exists.
2. AiCLI prompts `aicli clarification>`.
3. Terminal `input()` returns one physical line.
4. AiCLI strips it into `reply_text`.
5. AiCLI submits `[reply_text]` immediately.
6. Remaining pasted physical lines are consumed by later loop iterations.
7. Platform Core receives several independent messages.
8. The last fragment may become the approved `original_request`.

This exactly matches the observed approval fragment:

`original_request: No Human Interface behaviour shall change.`

## Ownership Analysis

Platform Core owns:

- clarification semantics.
- clarification sufficiency.
- replay-backed clarification continuity.
- development intent resolution.
- governance transition.

AiCLI owns:

- terminal input capture.
- terminal output rendering.
- forwarding one human reply to Platform Core.
- session lifecycle prompts.

Input aggregation is not semantic interpretation. Aggregating physical terminal lines until an explicit delimiter is a Human Interface capture responsibility, as long as AiCLI does not inspect or decide the meaning of the reply.

Therefore:

- Platform Core must receive the intended clarification reply as one message.
- AiCLI may aggregate physical lines into that one message.
- AiCLI must not decide whether the reply resolves clarification.
- AiCLI must not create approval, governance, replay, provider, or worker semantics.

## Should Clarification Replies Support Multi-Line Input?

Yes.

Clarification answers for governed development work often include:

- objective;
- constraints;
- ownership boundaries;
- non-goals;
- validation expectations;
- governance notes.

For large Generation 15 prompts, a single-line clarification answer is not sufficient UX. Multi-line clarification replies should be supported by input capture without changing Platform Core semantics.

## Minimal Fix Recommendation

Smallest architecturally correct correction:

Add clarification-reply composition inside AiCLI submit-mode continuation.

Recommended behavior:

1. When `pending_clarification is not None`, AiCLI enters a clarification compose loop.
2. It collects physical terminal lines into a local buffer.
3. It accepts `/send` or `.` as the explicit reply delimiter.
4. It preserves internal line breaks.
5. It supports `/cancel` before submission.
6. It submits the aggregated clarification reply exactly once through the existing `_submit_composed_request()` path.
7. Platform Core continues to decide whether clarification resolved.

This mirrors the already certified compose behavior for initial interactive requests and does not move semantics into AiCLI.

Do not fix this in Platform Core by trying to merge separate messages after the fact. Once AiCLI sends fragments as separate Platform Core submissions, replay and `original_request` evidence have already diverged from the human's intended single clarification reply.

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/cli/aicli.py aigol/runtime/platform_core_project_services.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- `python -m py_compile ...` passed.
- `python -m pytest -q` passed: `5819 passed, 4 skipped`.
- `git diff --check` passed.

## Files Modified

- `docs/governance/G15_HIR_04_CLARIFICATION_MULTI_LINE_REPLY_BINDING_AUDIT.md`

## Boundary Confirmation

No runtime behavior was changed.

No Platform Core semantics were changed.

No Human Interface semantic authority was introduced.

No governance, replay, provider, or worker ownership moved into AiCLI.

The recommended future correction is terminal input aggregation only.

## Final Determination

Multi-line clarification replies are split because AiCLI submit-mode clarification continuation reads and submits one physical terminal line at a time.

The smallest correct fix is an AiCLI clarification compose buffer that aggregates physical lines into one intended human reply before forwarding it to Platform Core.
