# G17-HI-02E - Approval Runtime Continuation Implementation Audit

Status: AUDIT COMPLETE

Date: 2026-07-09

Final verdict: CONTINUATION_HANDLING_INCOMPLETE

## Executive Summary

The observed contradiction is reproducible and localized to the `./aicli` interactive session loop before `/approve` is received.

Platform Core correctly returns an approval-preparation conversation object:

- `summary_admissible: True`
- `runtime_binding_admissible: True`
- `response_mode: APPROVAL_PREPARATION`
- `approval_state: PENDING_HUMAN_APPROVAL`
- `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME`

`./aicli` renders that summary and stores it as `pending_summary`. If the next physical read raises `EOFError` or `StopIteration` before `/approve`, the interactive loop takes the EOF branch, sets `exit_reason: EOF`, exits the loop, and emits the final session result with:

- `session_status: REFERENCE_UHI_SESSION_COMPLETED`
- `runtime_status: REFERENCE_UHI_RUNTIME_NOT_REQUIRED`
- `pending_approval: True`
- `runtime_entered: False`

The session closure is therefore not a Platform Core runtime decision. It is an incomplete Human Interface continuation handling path: EOF/end-of-input is treated as terminal even when Platform Core has an active pending approval continuation.

## Observed Runtime Evidence

Observed user-facing sequence:

```text
Governed implementation summary
runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME
Approval delegates to the certified runtime; the Human Interface does not authorize or execute.
Type /approve to continue, or /cancel to discard.

aicli session closed.
runtime_status: REFERENCE_UHI_RUNTIME_NOT_REQUIRED
```

Local reproduction using the current implementation:

```text
input sequence: ["Implement governance validation utility.", "/send"]
```

The input reader then raises `StopIteration`, simulating EOF after the approval summary is displayed.

Returned session object:

```text
exit_reason: EOF
session_status: REFERENCE_UHI_SESSION_COMPLETED
runtime_status: REFERENCE_UHI_RUNTIME_NOT_REQUIRED
pending_approval: True
runtime_entered: False
submitted_request_count: 1
approval_count: 0
summary_admissible: True
runtime_binding_admissible: True
conversation_response_mode: APPROVAL_PREPARATION
```

This exactly matches the reported contradiction: Platform Core created an approval continuation, while the Human Interface session closed before collecting approval.

## Runtime Result Analysis

There is no certified runtime result object at the time of premature session closure.

Implementation evidence:

- `aigol/cli/aicli.py` initializes `runtime_result = None` and `runtime_status = REFERENCE_UHI_NOT_REQUIRED`.
- The only interactive-mode branch that calls `run_human_interface_runtime_entry()` is the `/approve` branch.
- If `/approve` is not read, `runtime_result` remains `None`.
- Final result construction sets `runtime_entered` from `runtime_result is not None`.

Therefore the returned object is not a Platform Core Runtime result. It is an `aicli` session result containing a pending Platform Core approval summary and no runtime entry.

`REFERENCE_UHI_RUNTIME_NOT_REQUIRED` is therefore mechanically correct for the runtime-entry layer because Runtime Entry was never called. It is misleading as a user-facing continuation outcome because approval was still pending.

## Approval Continuation Analysis

Platform Core explicitly requests approval continuation.

Implementation evidence:

- `aigol/runtime/platform_core_project_services.py` sets `summary_admissible` when a deterministic governed development request is admissible and no clarification is required.
- The same resolution sets `runtime_binding_admissible = summary_admissible`.
- `human_conversation_experience_from_resolution()` sets `response_mode = APPROVAL_PREPARATION` when `summary_admissible` is true.
- `_conversation_approval_summary()` returns:
  - `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME`
  - `approval_state: PENDING_HUMAN_APPROVAL`
  - `requires_human_approval`
  - `canonical_runtime_prompt`
  - `human_interface_authorizes: False`
  - `human_interface_executes: False`

`./aicli` consumes that Platform Core object:

- `_submit_composed_request()` reads `project_context["development_intent_resolution"]`.
- It reads `project_context["human_conversation_experience"]`.
- When `resolution["summary_admissible"] is True`, it calls `_summary_from_conversation()`.
- `_summary_from_conversation()` requires `conversation["approval_summary"]`.
- `_render_summary()` renders `runtime_after_approval` and `Type /approve to continue, or /cancel to discard.`
- `_submit_composed_request()` returns that summary as `pending_summary`.

Thus Platform Core explicitly expresses a pending approval continuation and `./aicli` initially recognizes it.

## Session Termination Trace

Deterministic trace:

1. Human submits request.
   - Owner: Human Interface transport.
   - `./aicli` stores physical input lines in `compose_buffer`.

2. Human sends `/send`.
   - Owner: `./aicli` command handling.
   - Branch: `normalized in AICLI_SEND_COMMANDS`.
   - Action: `_submit_composed_request()`.

3. Platform Core prepares project context.
   - Owner: Platform Core.
   - Function: `prepare_unified_human_interface_project_context()`.
   - Returned object: `UNIFIED_HUMAN_INTERFACE_PROJECT_CONTEXT_ARTIFACT_V1`.
   - State: `human_conversation_experience.response_mode = APPROVAL_PREPARATION`.
   - Approval: `approval_summary.approval_state = PENDING_HUMAN_APPROVAL`.

4. `./aicli` renders summary.
   - Owner: Human Interface presentation.
   - Function: `_render_summary()`.
   - Text: `Type /approve to continue, or /cancel to discard.`
   - Local state: `pending_summary` becomes a dict; `pending_clarification` becomes `None`.

5. `./aicli` continues the while loop.
   - Owner: Human Interface session loop.
   - Expected next input: `/approve`, `/cancel`, or continued human input.

6. Input reader raises EOF/StopIteration.
   - Owner: Human Interface transport.
   - Branch: `except (EOFError, StopIteration)`.

7. EOF branch closes the loop.
   - Owner: `./aicli`.
   - Current code checks only `compose_buffer` before closing.
   - It does not check `pending_summary`.
   - It sets `exit_reason = "EOF"` and breaks.

8. Final session result is rendered.
   - Owner: `./aicli`.
   - `session_status = REFERENCE_UHI_SESSION_COMPLETED`.
   - `runtime_status` remains initial `REFERENCE_UHI_RUNTIME_NOT_REQUIRED`.
   - `pending_approval = True`.
   - `runtime_entered = False`.

## Implementation Ownership

The premature termination decision is made by `./aicli`, not Platform Core.

Evidence:

- Platform Core returned `APPROVAL_PREPARATION` and `PENDING_HUMAN_APPROVAL`.
- Runtime Entry is not called until the `/approve` branch.
- The EOF branch lives in `run_reference_uhi_session()`.
- The EOF branch exits regardless of `pending_summary`.
- Final rendering is `_render_session_result(result)`, which prints `aicli session closed.`

The relevant implementation path is:

```text
run_reference_uhi_session()
  -> /send branch
  -> _submit_composed_request()
  -> prepare_unified_human_interface_project_context()
  -> Platform Core approval_summary
  -> pending_summary set
  -> next input read
  -> EOF/StopIteration branch
  -> exit_reason = EOF
  -> break
  -> result session_status = REFERENCE_UHI_SESSION_COMPLETED
  -> runtime_status remains REFERENCE_UHI_RUNTIME_NOT_REQUIRED
```

## Root Cause

Root cause:

`./aicli` interactive mode lacks pending-approval continuation handling in its EOF/end-of-input branch.

The branch handles `compose_buffer` specially:

- If `compose_buffer` has content, it submits it before closing.
- If `compose_buffer` is empty, it closes the session.

The branch does not handle:

- `pending_summary is not None`
- `pending_clarification is not None`
- Platform Core `approval_state: PENDING_HUMAN_APPROVAL`
- Platform Core `response_mode: APPROVAL_PREPARATION`

As a result, an input-stream boundary is treated as session completion even while the Platform Core conversation state is waiting for approval continuation.

## Critical Investigation Answers

1. What exact runtime object is returned to `./aicli`?

No runtime object is returned in the premature closure case. The returned object is the final `aicli` session result. The Platform Core object before closure is a project context artifact containing `development_intent_resolution` and `human_conversation_experience`.

2. Does Platform Core explicitly request approval continuation?

Yes. It returns `response_mode: APPROVAL_PREPARATION`, `runtime_binding_admissible: True`, `approval_state: PENDING_HUMAN_APPROVAL`, and `runtime_after_approval: CERTIFIED_PLATFORM_CORE_RUNTIME`.

3. Which implementation branch closes the session?

The `except (EOFError, StopIteration)` branch in `run_reference_uhi_session()` closes the session after the approval summary if no `/approve` input arrives.

4. Is session closure based on runtime status, conversation state, approval state, end-of-loop logic, or missing continuation handling?

It is based on end-of-loop EOF handling and missing continuation handling. It is not based on Platform Core runtime status, conversation state, or approval state.

5. Does `./aicli` currently ignore approval continuation information?

Partially. It renders and stores `pending_summary`, and it correctly delegates to Runtime Entry if `/approve` is read. It ignores `pending_summary` when EOF/StopIteration occurs in interactive mode.

6. Is `REFERENCE_UHI_RUNTIME_NOT_REQUIRED` being interpreted correctly?

As an internal runtime-entry status, yes: Runtime Entry was not reached. As a session-level user-facing outcome while `pending_approval` is true, it is incomplete and misleading.

7. Should approval continuation prevent session termination?

In an interactive Human Interface session, yes. Pending approval should prevent declaring ordinary session completion. If the transport ends, the session should be represented as awaiting human approval or interrupted with pending approval, not completed with a runtime-not-required implication.

## Minimal Repair Assessment

No Platform Core redesign is required.

No Runtime redesign is required.

No Governance, Replay, PCCL, Provider, or Worker redesign is required.

The smallest repair surface is localized to `./aicli` interactive session continuation handling:

- The EOF/StopIteration branch should account for `pending_summary`.
- Pending approval should not be rendered as ordinary session completion.
- The result should distinguish `AWAITING_HUMAN_APPROVAL` or equivalent pending-continuation state from terminal completion.
- Runtime status should not be used as the only human-facing signal when runtime entry has not yet occurred because approval is pending.

This is not a recommendation to implement in this audit. It identifies the implementation repair boundary.

## Architectural Impact

The issue confirms G17-HI-02A and G17-HI-02B:

- Platform Core owns approval semantics and runtime continuation eligibility.
- `./aicli` currently owns too much live conversation lifecycle mechanics.
- The missing shared conversation boundary would make pending approval an explicit Platform Core state and prevent interface-local EOF handling from being mistaken for conversation completion.

Architecturally, this is a Human Interface continuation handling defect, not a Platform Core capability gap.

## Final Recommendation

Treat the defect as localized continuation handling incomplete in `./aicli`.

Future implementation should preserve thin-interface boundaries:

- Do not move approval semantics into `./aicli`.
- Do not reinterpret Human Intent Resolution.
- Do not alter Runtime Entry semantics.
- Do not change Governance, Replay, PCCL, Provider, or Worker responsibilities.
- Make `./aicli` honor existing Platform Core pending approval state when deciding whether a session is complete, awaiting input, or interrupted.

## Final Verdict

CONTINUATION_HANDLING_INCOMPLETE

The premature session termination is caused by the `./aicli` interactive EOF/end-of-input branch closing the session while `pending_summary` remains active. Platform Core explicitly requested approval continuation, and the approved path enters the certified runtime when `/approve` is supplied. The incomplete implementation path is therefore the Human Interface approval-continuation wait/termination handling, not Runtime Entry, Governance, Replay, PCCL, Provider, or Worker behavior.
