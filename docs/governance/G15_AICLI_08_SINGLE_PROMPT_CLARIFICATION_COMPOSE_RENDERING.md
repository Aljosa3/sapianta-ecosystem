# G15-AICLI-08 - Single Prompt Clarification Compose Rendering

Status: IMPLEMENTED
Date: 2026-07-07
Scope: AiCLI terminal rendering lifecycle for clarification compose mode.

## Executive Summary

G15-AICLI-08 implements the smallest Human Interface fix identified by G15-AICLI-07:

AICLI_CLARIFICATION_COMPOSE_PROMPT_RENDERING_REPEATS_DURING_PASTE

Clarification compose mode now renders the visible clarification prompt only once. After the first physical line is captured, subsequent reads use an empty prompt until `/send`, `.`, `/cancel`, `/exit`, or EOF.

Platform Core is unchanged.

## Knowledge Reuse Audit

Existing implementation reused:

- `_read_clarification_reply()`
  - remains the single clarification compose buffer.
  - continues to preserve line ordering and internal line breaks.
  - continues to detect `/send`, `.`, `/cancel`, `/exit`, and EOF.
- `_split_input_chunk()`
  - remains the deterministic chunk splitter when an input reader returns multiple lines at once.
- `_submit_composed_request()`
  - remains the only path that forwards composed clarification text to Platform Core.
- Existing submit-mode tests
  - were retained and extended to cover line-by-line terminal paste behavior.

No new compose implementation was introduced.

## Architectural Review

AiCLI owns:

- terminal prompt rendering.
- terminal input capture.
- local compose buffering.
- local command delimiters.

Platform Core owns:

- clarification semantics.
- Human Intent Resolution.
- governance.
- replay.
- approval.
- runtime orchestration.
- Canonical Semantic Artifact creation and gating.

The implementation changes only prompt rendering. AiCLI still does not inspect semantic content or decide whether clarification is sufficient.

## Implementation Summary

Changed:

- `_read_clarification_reply()` now calls:
  - `input_reader("aicli clarification> ")` before the first line.
  - `input_reader("")` for all subsequent physical reads while the clarification buffer is non-empty.

Unchanged:

- `/send` and `.` submit the composed reply.
- `/cancel` discards the pending clarification.
- `/exit` is passed back as a local exit intent.
- EOF records awaiting human input.
- composed replies are forwarded once to Platform Core.
- Platform Core remains the clarification authority.

## Regression Test Summary

Updated:

- `tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py`

New coverage:

- simulates real terminal line-by-line paste.
- records prompts passed to the input reader.
- proves only the first clarification read uses `aicli clarification> `.
- proves subsequent line reads use an empty prompt.
- proves `aicli clarification compose> ` is not rendered.
- proves the aggregated reply is submitted once and preserved as the Platform Core `raw_prompt`.

Focused validation:

- `15 passed`.

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/cli/aicli.py`
- `python -m pytest -q tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g15_hir_02_replay_backed_clarification_continuity.py tests/test_g15_aicli_02_submission_mode.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- Focused validation passed: `15 passed`.
- Full repository validation passed: `5822 passed, 4 skipped`.
- Diff whitespace validation passed.

## Files Modified

- `aigol/cli/aicli.py`
- `tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py`
- `docs/governance/G15_AICLI_08_SINGLE_PROMPT_CLARIFICATION_COMPOSE_RENDERING.md`

## Boundary Confirmation

No Platform Core code was changed.

No Human Intent Resolution behavior was changed.

No governance, replay, approval, runtime orchestration, provider, worker, or Canonical Semantic Artifact ownership was changed.

AiCLI remains a thin Human Interface and owns only terminal input/rendering behavior.

## Final Determination

Clarification compose rendering is now single-prompt.

AiCLI no longer renders `aicli clarification compose>` between pasted physical lines. Multi-line clarification replies can be pasted or typed, submitted once with `/send` or `.`, and forwarded to Platform Core as one composed message.
