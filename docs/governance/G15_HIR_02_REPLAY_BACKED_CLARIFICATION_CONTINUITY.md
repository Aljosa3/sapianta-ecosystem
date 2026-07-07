# G15-HIR-02 - Replay-Backed Clarification Continuity

Status: IMPLEMENTED
Date: 2026-07-07
Scope: Platform Core UHI clarification continuity binding.

## Executive Summary

G15-HIR-02 implements the missing stage identified by G15-HIR-00:

PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_STAGE_MISSING

Clarification replies received through Unified Human Interfaces now bind to replay-backed pending clarification state recorded by Platform Core workspace services. The reply is no longer treated as an unqualified fresh governed request while a Platform Core clarification is active.

AiCLI remains unchanged as a semantic boundary. It still captures input, renders Platform Core output, forwards replies, and delegates approved runtime execution.

## Knowledge Reuse Audit

Existing implementation reused:

- `record_unified_human_interface_workspace_state()`
  - already records `pending_clarification_request` in Platform Core workspace replay.
- `latest_platform_core_workspace_state()`
  - already restores the latest replay-backed project state for UHI project services.
- `resolve_development_intent()`
  - remains the deterministic resolver for whether a clarification reply is sufficiently concrete for governed summary preparation.
- `human_conversation_experience_from_resolution()`
  - remains the Platform Core owner of clarification and approval-facing conversation output.
- Existing AiCLI submit flow
  - continues to call `_submit_composed_request()` and does not gain clarification semantics.

No duplicate HIRR or conversational runtime resolver was introduced.

## Architectural Review

The implementation preserves Generation 14 boundaries:

- Platform Core owns clarification continuity.
- Platform Core owns development intent resolution.
- Platform Core owns workspace replay and replay lineage.
- Human Interfaces do not inspect clarification semantics.
- AiCLI does not decide whether a reply is sufficient.
- Provider Platform is unchanged.
- Worker Platform is unchanged.
- Governance authority remains downstream of approval and certified runtime entry.

The new continuity stage lives in `aigol/runtime/platform_core_project_services.py`, the existing owner of UHI project services.

## Implementation Summary

New Platform Core behavior:

1. `prepare_unified_human_interface_project_context()` restores prior workspace replay.
2. Platform Core checks for `pending_clarification_request`.
3. If present, Platform Core recovers a replay-backed active UHI clarification state.
4. The human reply is bound to that active clarification state.
5. Platform Core records a `PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_ARTIFACT_V1` artifact under `uhi_clarification_continuity`.
6. The existing deterministic `resolve_development_intent()` result is enriched with continuity metadata.
7. If the reply is sufficient, approval preparation proceeds.
8. If the reply is still insufficient, clarification remains active and no new governed request is created.

New implementation points:

- `PLATFORM_CORE_UHI_CLARIFICATION_CONTINUITY_VERSION`
- `replay_backed_uhi_clarification_state()`
- `resolve_uhi_clarification_continuity()`
- `next_uhi_clarification_continuity_index()`

New deterministic evidence fields include:

- `reply_bound_to_active_clarification`
- `clarification_continuity_status`
- `clarification_resolved`
- `new_governed_request_created`
- `active_clarification_workspace_state_reference`
- `active_clarification_workspace_state_hash`
- `semantic_lineage_preserved`
- `replay_lineage_preserved`
- `human_interface_authority = false`

## Clarification Continuity Validation

Regression coverage proves:

- a sufficient clarification reply binds to the replay-backed pending clarification state.
- the reply resolves clarification and prepares the governed implementation summary.
- an insufficient reply remains bound to the same clarification continuity path.
- insufficient replies do not create a new governed request.
- subsequent sufficient replies resolve the same Platform Core conversation.
- AiCLI remains non-authoritative.

Implemented tests:

- `tests/test_g15_hir_02_replay_backed_clarification_continuity.py`

Existing submit-mode and project-service tests still pass:

- `tests/test_g15_aicli_03_persistent_platform_conversation_session.py`
- `tests/test_g15_aicli_02_submission_mode.py`
- `tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py`
- `tests/test_g14_22_reference_unified_human_interface_v1.py`
- `tests/test_g14_05_persistent_development_workspace_v1.py`
- `tests/test_g14_08a_platform_core_project_services_extraction_v1.py`

## Validation Summary

Validation commands executed:

- `python -m py_compile aigol/runtime/platform_core_project_services.py aigol/cli/aicli.py`
- `python -m pytest -q tests/test_g15_hir_02_replay_backed_clarification_continuity.py tests/test_g15_aicli_03_persistent_platform_conversation_session.py tests/test_g15_aicli_02_submission_mode.py`
- `python -m pytest -q tests/test_g14_27_unified_human_interface_runtime_project_services_v1.py tests/test_g14_22_reference_unified_human_interface_v1.py tests/test_g14_05_persistent_development_workspace_v1.py tests/test_g14_08a_platform_core_project_services_extraction_v1.py`
- `python -m pytest -q`
- `git diff --check`

Validation result:

- Compile passed.
- Focused G15 submit/HIR tests passed: `12 passed`.
- Nearby G14 project-services tests passed: `14 passed`.
- Full repository validation passed: `5819 passed, 4 skipped`.
- Diff whitespace validation passed.

## Files Modified

- `aigol/runtime/platform_core_project_services.py`
- `tests/test_g15_hir_02_replay_backed_clarification_continuity.py`
- `docs/governance/G15_HIR_02_REPLAY_BACKED_CLARIFICATION_CONTINUITY.md`

## Boundary Confirmation

AiCLI remains a thin adapter:

- no clarification resolver was added to AiCLI.
- no semantic sufficiency rules were added to AiCLI.
- no governance decision moved into AiCLI.
- no provider or worker behavior changed.

Platform Core remains the sole owner of Human Intent Resolution and clarification continuity.

## Final Determination

Replay-backed UHI clarification continuity is implemented.

Clarification replies now bind to the active Platform Core clarification context recorded in workspace replay. When the reply is sufficient, Platform Core can continue toward governed summary and approval. When the reply is insufficient, Platform Core keeps clarification active without treating the answer as a new governed request.
