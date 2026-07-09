# G17-HI-02F — AiCLI Approval Continuation Handling Implementation

Status: implemented

Date: 2026-07-09

Final verdict: AICLI_APPROVAL_CONTINUATION_HANDLING_HARDENED

## Summary

This implementation hardens `./aicli` interactive approval continuation handling.

When Platform Core returns a governed approval summary and the next interactive read reaches EOF or `StopIteration`, `./aicli` now records the session as awaiting human approval instead of reporting a completed session with the initial runtime status.

## Root Cause Addressed

The interactive EOF branch in `aigol/cli/aicli.py` only checked `compose_buffer`.

If EOF occurred after Platform Core had returned a pending approval summary, the branch set `exit_reason: EOF`, rendered the session as completed, and left `runtime_status` at `REFERENCE_UHI_RUNTIME_NOT_REQUIRED` even though `pending_approval` was still true.

## Files Changed

- `aigol/cli/aicli.py`
- `tests/test_g15_aicli_01_compose_runtime_stability.py`
- `docs/governance/G17_HI_02F_AICLI_APPROVAL_CONTINUATION_HANDLING_IMPLEMENTATION.md`

## Boundary Preservation Statement

The change is limited to Human Interface adapter state reporting and terminal interruption handling.

`./aicli` still does not authorize, execute, certify, select providers, own replay, own governance, own PCCL, or own Platform Core workflow semantics. It only preserves and reports the pending Platform Core approval artifact already returned by `prepare_unified_human_interface_project_context`.

`/approve` continues to delegate to `run_human_interface_runtime_entry` or the injected runtime runner. `/cancel` continues to discard pending local Human Interface interaction state.

## Validation Performed

- Pending approval EOF path covered by focused test.
- Pending approval cancellation covered by focused test.
- Existing approval delegation and compose hardening tests retained.
- Validation command results:
  - `python -m pytest tests/test_g15_aicli_01_compose_runtime_stability.py tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g15_aicli_02_submission_mode.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g15_hir_05_multi_line_clarification_compose_buffer.py tests/test_g15_runtime_06_governed_development_runtime_continuation.py -q`
  - Result: 31 passed.
  - `git diff --check`
  - Result: clean.

## Final Result

EOF or `StopIteration` during a pending Platform Core approval no longer falsely reports a completed interactive session. The result now preserves `pending_approval: True`, uses `exit_reason: EOF_AWAITING_APPROVAL`, and records `session_status: REFERENCE_UHI_SESSION_AWAITING_HUMAN_APPROVAL`.

AICLI_APPROVAL_CONTINUATION_HANDLING_HARDENED
