# G15-HIR-07 - Clarification Resolution State Management

Status: IMPLEMENTED

Milestone: G15-HIR-07

Scope: Platform Core clarification state management. AiCLI, governance semantics, replay semantics, Human Intent Resolution semantics, runtime routing, approval, and worker/runtime ownership were preserved.

## Knowledge Reuse Audit

Existing certified capabilities reused:

- Human Intent Resolution and Development Intent Resolution in `aigol/runtime/platform_core_project_services.py`.
- Replay-backed UHI clarification continuity through `replay_backed_uhi_clarification_state(...)`.
- Existing clarification compose and `/send` behavior in `aigol/cli/aicli.py`.
- Persistent workspace snapshots through `record_unified_human_interface_workspace_state(...)`.
- Runtime Entry through `run_human_interface_runtime_entry(...)`.
- Existing immutable replay evidence through `write_json_immutable(...)` and `replay_hash(...)`.

No replacement clarification runtime, Human Interface logic, replay path, governance path, or runtime selector was introduced.

## Architectural Review

Clarification state is Platform Core-owned:

1. AiCLI captures text and forwards one composed clarification reply.
2. Platform Core restores `pending_clarification_request` from workspace replay.
3. Platform Core binds the submitted reply to the active clarification.
4. Platform Core determines whether the active clarification is resolved.
5. Platform Core records replay-visible clarification continuity.
6. Platform Core clears pending clarification by returning an approval summary instead of another clarification request.

AiCLI remains a thin Human Interface. It does not assign question identifiers, interpret answers, clear semantic state, or decide whether clarification is resolved.

## Root Cause Analysis

The repeated clarification was caused by incomplete clarification resolution state management.

Findings:

- Clarification questions did not have deterministic question identifiers.
- The submitted clarification answer was bound to the active clarification as a whole, but not to stable question slots.
- Platform Core resolved the clarification reply as a standalone development request.
- Short deterministic answers to the asked slots could be forwarded successfully but still fail standalone development intent detection.
- When that happened, Platform Core preserved the pending clarification state and reopened the same questions.

Deterministic cause:

`CLARIFICATION_REPLY_RESOLVED_AS_STANDALONE_REQUEST_INSTEAD_OF_BOUND_SLOT_ANSWER`

This was not an AiCLI compose issue and not a runtime routing issue.

## Implementation Summary

Implemented the smallest Platform Core correction in `aigol/runtime/platform_core_project_services.py`:

- Added deterministic clarification question bindings derived from question text.
- Restored active clarification state now includes `clarification_question_bindings`.
- Clarification continuity artifacts record:
  - `reply_resolution_source`,
  - `clarification_question_bindings`,
  - `answered_clarification_question_ids`.
- If a standalone reply is not runtime-admissible but substantively answers the active clarification slots, Platform Core resolves a governed development request assembled from:
  - original request,
  - active clarification questions,
  - submitted clarification answer.
- Non-substantive replies still remain clarification-bound.

The fix consumes resolved clarification state without allowing AiCLI to own semantic interpretation.

## Validation Summary

Validation commands required:

- `python -m py_compile`
- `python -m pytest -q`
- `git diff --check`

Validation results:

- Focused clarification regression passed: `9 passed in 0.19s`.
- `python -m py_compile aigol/runtime/platform_core_project_services.py aigol/cli/aicli.py tests/test_g15_hir_07_clarification_resolution_state_management.py` passed.
- `python -m pytest -q` passed: `5830 passed, 4 skipped in 140.29s`.
- `git diff --check` passed before and after validation-section update.

## Regression Test Summary

Added:

- `tests/test_g15_hir_07_clarification_resolution_state_management.py`

The regression reproduces:

1. A clarification-producing initial request.
2. A deterministic answer to the clarification slots.
3. `/send`.
4. Continuation to approval/runtime.
5. No repeated clarification after resolution.

The test also verifies replay evidence:

- question bindings exist,
- answered question IDs are recorded,
- continuity replay reports `clarification_resolved: true`,
- pending clarification is removed from the latest workspace state.

## Files Modified

- `aigol/runtime/platform_core_project_services.py`
- `tests/test_g15_hir_07_clarification_resolution_state_management.py`
- `docs/governance/G15_HIR_07_CLARIFICATION_RESOLUTION_STATE_MANAGEMENT.md`

## Boundary Confirmation

Preserved boundaries:

- AiCLI remains input/render/delegation only.
- Platform Core remains sole owner of clarification semantics and state.
- Human Intent Resolution semantics were reused, not redesigned.
- Replay remains immutable and authoritative.
- Governance, approval, runtime routing, worker ownership, and runtime orchestration were unchanged.

## Governance Report

G15-HIR-07 confirms that repeated identical clarification questions were caused by missing deterministic slot-level clarification resolution state.

The implemented correction records stable clarification question identifiers, binds the submitted answer to those identifiers, and consumes the pending clarification when Platform Core determines that the answer resolves the active clarification.

Certification conclusion:

`G15_HIR_07_CLARIFICATION_RESOLUTION_STATE_MANAGEMENT_IMPLEMENTED`
