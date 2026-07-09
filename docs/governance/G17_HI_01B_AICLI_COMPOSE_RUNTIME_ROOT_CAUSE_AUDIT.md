# G17-HI-01B - AiCLI Compose Runtime Root Cause Audit

Status: HARDENING RECOMMENDED

Date: 2026-07-09

Milestone: G17-HI-01B

Scope: Audit-only implementation root cause review of the current `./aicli` compose runtime. This milestone does not implement fixes, redesign Platform Core, redesign Human Interface architecture, introduce Platform UX contracts, introduce runtime services, or review Governance, Replay, PCCL, or Platform Core behavior.

## Executive Summary

The observed compose-mode behavior is caused by a line-oriented terminal input loop in `run_reference_uhi_session()` that renders a visible prompt before each physical `input()` read.

Root cause:

```text
LINE_ORIENTED_INPUT_PROMPT_RENDERING_WITH_REAL_TERMINAL_PASTE
```

When `input()` receives a large paste as one returned string containing newlines, `_split_input_chunk()` handles it deterministically and suppresses prompt flooding by processing `pending_input_lines`.

When a real terminal delivers the same paste one physical line at a time, `pending_input_lines` is empty after each line. The loop calls:

```python
input_reader("aicli compose> " if compose_buffer else "aicli> ")
```

again while the paste is still being delivered. The terminal can then display `aicli compose>` between echoed pasted lines. This creates the observed visual corruption, uncertainty about submission state, and apparent compose-mode continuation.

Final recommendation:

```text
HARDENING RECOMMENDED
```

Replacement is not justified by the implementation evidence. The defect is concentrated in Human Interface terminal input handling and prompt rendering. The CLI remains thin and does not contain Platform Core business logic.

## Observed Behaviour

Observed symptoms:

- repeated `aicli compose>` prompt rendering;
- multiline paste corruption;
- prompt fragments appearing inside pasted text;
- compose mode continuing unexpectedly;
- uncertainty regarding whether `/send` was received;
- manual Ctrl+C interruption;
- `KeyboardInterrupt` inside `run_reference_uhi_session()` -> `input_reader()` -> `input()`.

Observed behavior matches the known terminal pattern where a pasted multi-line payload can be delivered to Python `input()` one completed line at a time while the terminal is also echoing text and the program is printing prompts.

## Implementation Review

Reviewed implementation surfaces:

- `aigol/cli/aicli.py::run_reference_uhi_session()`
- `aigol/cli/aicli.py::run_reference_uhi_submit_session()`
- `aigol/cli/aicli.py::_read_clarification_reply()`
- `aigol/cli/aicli.py::_split_input_chunk()`
- `aigol/cli/aicli.py::_normalize_submit_request()`
- `aigol/cli/aicli.py::_submit_composed_request()`
- compose-mode and paste regression tests.

Relevant implementation evidence:

- `run_reference_uhi_session()` initializes `compose_buffer` and `pending_input_lines`.
- The outer loop reads from `pending_input_lines` first.
- If no pending lines exist, it calls `input_reader("aicli compose> " if compose_buffer else "aicli> ")`.
- It splits returned chunks with `_split_input_chunk()`.
- It submits only when normalized input equals `/send` or `.`.
- It catches `EOFError` and `StopIteration`.
- It does not catch `KeyboardInterrupt`.
- Submit mode reads the whole request with `sys.stdin.read()` before Platform Core submission.
- Clarification reply mode has already been hardened to use an empty prompt after the first physical line.

## Input Lifecycle Analysis

Interactive compose lifecycle:

1. `compose_buffer` starts empty.
2. The loop calls `input_reader("aicli> ")`.
3. A non-command line is appended to `compose_buffer`.
4. On the next physical read, the loop calls `input_reader("aicli compose> ")`.
5. If a returned chunk contains multiple lines, `_split_input_chunk()` stores them in `pending_input_lines`.
6. While `pending_input_lines` is non-empty, the loop consumes those lines without calling `input_reader()` and without rendering another prompt.
7. If the terminal returns one line per call, `pending_input_lines` becomes empty after every line and the visible prompt is rendered again before the next line.

This lifecycle is deterministic in code but unstable in real terminal paste scenarios.

Submit mode lifecycle:

1. `run_reference_uhi_submit_session()` prints submit instructions.
2. It reads the complete request through `stdin_reader` or `sys.stdin.read()`.
3. `_normalize_submit_request()` normalizes line endings and strips surrounding blank lines.
4. It submits the complete request once.

Submit mode avoids the compose-mode defect because it does not interleave visible prompts with pasted lines.

## Compose State Analysis

`compose_buffer` lifecycle is mostly correct:

- appends non-command lines;
- preserves blank lines after composition has started;
- clears after `/send`, `.`, `/approve`-triggered submission, or `/cancel`;
- submits on EOF when non-empty;
- records `unsubmitted_compose_line_count` after session closure.

Deterministic state transitions:

- empty input before composition is ignored;
- `/send` and `.` submit only when the buffer is non-empty;
- `/exit` is blocked while the buffer is non-empty;
- `/cancel` clears local compose state and pending rendered state;
- `/approve` submits any buffered request first, then approves only if a Platform Core summary exists.

No evidence shows semantic state corruption or Platform Core state migration into `./aicli`.

The user-visible inconsistency is caused by terminal rendering and command delivery, not by nondeterministic internal state.

## Prompt Rendering Analysis

The repeated prompt is generated at:

```python
line = input_reader("aicli compose> " if compose_buffer else "aicli> ")
```

Prompt rendering and input collection are not cleanly separated in interactive compose mode. The prompt is passed directly into `input()`, which both displays the prompt and waits for one line of input.

This design is acceptable for short typed requests but fragile for pasted multiline content.

Clarification reply mode already demonstrates a safer pattern:

```python
line = input_reader("aicli clarification> " if not reply_buffer else "")
```

That implementation renders the clarification prompt once, then reads later physical lines with an empty visible prompt. The main compose loop has not received the same hardening.

## Session Loop Analysis

The session loop is deterministic but overloaded:

- it owns local compose state;
- it handles terminal commands;
- it submits composed text to Platform Core;
- it stores pending Platform Core summaries and clarifications;
- it approves pending summaries;
- it closes and records workspace state.

This is still a thin Human Interface implementation because it delegates all semantics and runtime behavior. However, the loop mixes prompt rendering, input collection, command handling, session transitions, and Platform Core submission in one function. That creates maintainability risk and makes terminal hardening harder than it needs to be.

EOF handling:

- EOF with a non-empty compose buffer submits the composed request to Platform Core, then closes.
- EOF with no buffer closes.
- Submit mode EOF is the normal completion mechanism for stdin capture.
- EOF during clarification or approval in submit mode records an awaiting-human-input status.

Ctrl+C handling:

- `KeyboardInterrupt` is not caught in `run_reference_uhi_session()`.
- The stack trace inside `input()` is therefore expected when the human interrupts a stuck or confusing compose session.
- This is a localized input handling bug, not a Platform Core defect.

## Root Cause Findings

1. Repeated prompt generation is caused by visible prompt rendering before each physical `input()` read while `compose_buffer` is non-empty.

2. `_split_input_chunk()` works only when a single `input_reader()` call returns multiple lines. It cannot suppress prompts between separate real terminal `input()` calls.

3. Real terminal paste behavior contributes directly. The terminal may deliver pasted content line by line while Python prints prompts between reads.

4. `/send` processing is deterministic only when `/send` is received as a clean standalone line. Visual prompt interleaving can make the human believe `/send` was not accepted, even when the code path is deterministic.

5. Ctrl+C produces a stack trace because `KeyboardInterrupt` is not handled in the compose loop.

6. Ctrl+D / EOF handling is deterministic, but EOF-with-buffer auto-submission can surprise users who expect EOF to cancel rather than submit.

7. The current state machine does not show evidence of semantic inconsistency. The observed inconsistency is presentation/input lifecycle ambiguity.

8. The implementation does not violate thin Human Interface architecture. It remains local input capture, rendering, and delegation.

## Classification Matrix

| Finding | Classification | Evidence | Assessment |
| --- | --- | --- | --- |
| Repeated `aicli compose>` prompt during line-by-line paste | D. Prompt rendering bug | `run_reference_uhi_session()` passes `aicli compose> ` to `input_reader()` whenever `compose_buffer` is non-empty. | Local prompt lifecycle defect. |
| Prompt fragments visually appearing inside pasted content | E. Terminal integration issue | Real terminals can echo paste content while Python prints prompts between line reads. | Terminal behavior amplifies the local prompt-rendering design. |
| Large pasted chunk returned in one call works | C. Input handling bug | `_split_input_chunk()` plus `pending_input_lines` suppress prompts only within one returned chunk. | Test coverage models chunked paste, not all real PTY paste behavior. |
| Multiline paste returned one line at a time remains noisy | F. Architectural implementation issue | The main loop uses prompt-driven `input()` as the multiline composition transport. | The implementation design is fragile for large paste even though the architecture remains thin. |
| Compose mode appears to continue unexpectedly | D. Prompt rendering bug | The loop continues until `/send`, `.`, `/cancel`, `/approve`, EOF, or `/exit` under allowed conditions. | The state machine is deterministic; presentation makes state unclear. |
| `/send` requires a clean standalone normalized line | C. Input handling bug | `normalized in AICLI_SEND_COMMANDS` is the only submit trigger. | Correct for command semantics, fragile when terminal paste/echo obscures delivery. |
| Ctrl+C emits stack trace | A. Localized implementation bug | `run_reference_uhi_session()` catches `EOFError` and `StopIteration`, not `KeyboardInterrupt`. | Local interrupt handling missing. |
| Ctrl+D with non-empty compose buffer submits then exits | F. Architectural implementation issue | EOF branch submits `compose_buffer` before closing. | Deterministic and tested, but surprising UX for users expecting cancel. |
| `compose_buffer` clear after submit/cancel | No defect | `compose_buffer.clear()` appears after `/send`, `/approve` pre-submit, EOF submit, and `/cancel`. | Lifecycle is internally coherent. |
| Thin-interface architecture | No defect | AiCLI delegates through `prepare_unified_human_interface_project_context(...)`, `run_human_interface_runtime_entry(...)`, and workspace-state recording. | No Platform Core authority migrated into `./aicli`. |

## Technical Debt Assessment

Technical debt level:

```text
MODERATE_LOCAL_HUMAN_INTERFACE_TECHNICAL_DEBT
```

Debt sources:

- main compose loop combines input capture, prompt rendering, command handling, submission, approval, and session closure;
- prompt rendering is coupled to blocking `input()` calls;
- large paste support depends on whether the input reader returns a multi-line chunk or one line per call;
- Ctrl+C is not handled gracefully;
- EOF semantics are deterministic but user-surprising;
- submit mode and clarification mode contain safer patterns not yet consistently applied to main compose mode.

Debt boundaries:

- no governance logic in `./aicli`;
- no runtime orchestration in `./aicli`;
- no replay ownership in `./aicli`;
- no provider selection in `./aicli`;
- no PCCL responsibility in `./aicli`.

## Repair vs Replacement Assessment

Critical question:

Can the existing `./aicli` implementation be cleanly hardened while preserving the current architecture?

Answer:

```text
YES
```

Evidence supporting repair:

- the failure is concentrated in one implementation region: `run_reference_uhi_session()` input/prompt lifecycle;
- clarification reply mode already demonstrates the viable hardening pattern by using an empty prompt after the first physical line;
- submit mode already provides a robust stdin transport for large pasted prompts;
- `_submit_composed_request()` is a clean delegation boundary into Platform Core;
- tests already isolate prompt recording, large chunks, EOF, `/send`, `.`, and cancellation behavior;
- source-level thin-adapter tests confirm no Platform Core authority is embedded in `./aicli`.

Evidence against replacement:

- no semantic contamination was found;
- no runtime or governance authority migrated into the CLI;
- no replay or certification responsibility migrated into the CLI;
- no evidence shows an unrecoverable state-machine model;
- current defects are localized to prompt rendering, terminal integration, interrupt handling, and UX clarity.

Replacement would be higher risk than hardening because a new CLI would need to preserve all existing delegation, workspace-state, submit-mode, clarification, approval, EOF, and replay-visible session behaviors.

## Architectural Impact

The implementation does not violate the intended thin Human Interface architecture.

AiCLI owns:

- terminal input capture;
- local compose buffering;
- command delimiter recognition;
- prompt rendering;
- forwarding complete requests and approval events to Platform Core.

AiCLI does not own:

- Human Intent Resolution;
- clarification semantics;
- knowledge reuse;
- governance;
- replay;
- certification;
- runtime orchestration;
- provider selection;
- PCCL responsibilities.

Architectural impact verdict:

```text
THIN_INTERFACE_ARCHITECTURE_PRESERVED_WITH_LOCAL_INPUT_RENDERING_DEFECTS
```

## Final Recommendation

Recommendation:

```text
HARDENING RECOMMENDED
```

Recommended future hardening scope:

- render compose instructions once, then use empty prompts for subsequent physical lines while the compose buffer is non-empty;
- handle `KeyboardInterrupt` as a local cancel/abort path without stack trace;
- make EOF behavior explicit in prompts and output;
- keep submit mode as the preferred path for large pasted requests;
- add line-by-line paste regression coverage for main compose mode, matching the existing clarification prompt recording test;
- avoid moving any Platform Core semantics into `./aicli`.

Replacement is not recommended unless future evidence shows state corruption, semantic duplication, or inability to preserve existing runtime delegation through localized hardening.

## Final Verdict

Final verdict:

```text
HARDENING RECOMMENDED
```

The deterministic root cause is local to `./aicli` input handling, terminal prompt rendering, and interrupt handling. The implementation should be hardened in place rather than replaced. Platform Core, Governance, Replay, PCCL, and runtime ownership are not implicated.
