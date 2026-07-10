# G17-HI-09 - Governed Development Worker Invocation Binding Implementation

## Executive Summary

G17-HI-09 investigated the reported Human Interface runtime sequence where the governed development proposal artifact showed `worker_invoked = false` after approval. The deterministic implementation evidence shows that the cited proposal artifact is an approval-required pre-execution capture, not the terminal certified runtime result.

The existing certified continuation already invokes the Worker lifecycle through the governed development bridge. The minimal correction implemented in this pass hardens the Human Interface runtime projection so worker and replay milestones are bound from the certified continuation envelope as well as the nested Worker lifecycle artifact. This preserves the existing Worker Platform, Governance, Replay, Platform Core, and Human Interface boundaries.

## Runtime Evidence

Observed proposal capture:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/acli_governed_development_execution_bridge/000_acli_governed_development_proposal_recorded.json`
- `artifact_type = ACLI_GOVERNED_DEVELOPMENT_BRIDGE_PROPOSAL_CAPTURE_V1`
- `bridge_status = APPROVAL_REQUIRED`
- `approval_required = true`
- `worker_invoked = false`

Observed certified continuation in the same turn:

- `.runtime/aicli/AICLI-REFERENCE-SESSION/TURN-000019/governed_bridge_certified_development_continuation/worker_lifecycle_continuation/worker_invocation/002_invocation_artifact_recorded.json`
- `artifact_type = WORKER_INVOCATION_ARTIFACT_V1`
- `invocation_status = WORKER_INVOKED`
- `worker_invoked = true`

Additional certified continuation evidence:

- `003_invocation_result_recorded.json` records `WORKER_INVOCATION_RESULT_ARTIFACT_V1`, `invocation_status = WORKER_INVOKED`, and `worker_invoked = true`.
- `openai_external_worker_provider/003_openai_external_worker_returned.json` records that the external worker provider boundary was reached and failed closed on local provider availability.
- `turn_completion/001_result_delivered.json` records `RESULT_DELIVERED_ARTIFACT_V1` with `result_delivered = true`.

## Worker Invocation Analysis

The canonical Human Interface approval path is:

1. `aigol/cli/aicli.py` records `/approve`.
2. `aigol/cli/aicli.py` delegates to `run_human_interface_runtime_entry(...)`.
3. `aigol/runtime/human_interface_runtime_entry_service.py` invokes the governed runtime runner with `operator_context = CANONICAL_HUMAN_INTERFACE_RUNTIME_ENTRY` and `auto_continue = true`.
4. `aigol/cli/aigol_cli.py` selects the governed development bridge before native conversational routing.
5. `_continue_governed_development_bridge_to_certified_runtime(...)` continues the approval-required proposal into the certified runtime.
6. `_continue_ppp_handoff_to_worker_request(...)` creates the Worker invocation request and calls `_continue_worker_request_to_replay_certification(...)`.
7. Worker invocation, result validation, and replay certification artifacts are recorded by the existing Worker lifecycle.

`worker_execution_required` becomes materially true when the governed development continuation reaches the implementation handoff and creates a Worker invocation request. The proposal artifact remains pre-execution by design and therefore records no Worker invocation.

## Root Cause

The implementation root cause was a projection weakness, not a missing Worker invocation service.

The Worker lifecycle was already invoked by `_continue_ppp_handoff_to_worker_request(...)`, but the Human Interface turn summary previously read several reached flags only from the nested `worker_lifecycle_continuation` map. If the certified continuation envelope carried the authoritative reached flags while the nested lifecycle map was incomplete, Human Interface runtime binding could under-report Worker/replay completion even though the existing Worker path had been selected.

## Implementation Summary

Implemented the smallest deterministic correction in `aigol/cli/aigol_cli.py`:

- Added `_continuation_flag_reached(...)` as a local projection helper.
- Updated `_worker_lifecycle_continuation_output(...)` to render reached flags from either the certified Worker continuation or the nested lifecycle artifact.
- Updated `_interactive_acli_governed_development_bridge_turn_summary(...)` so `worker_invoked`, Worker milestone flags, provider boundary reach, result validation reach, replay certification reach, and replay lineage preservation bind from the certified continuation envelope and the nested Worker lifecycle.

No new Worker, runtime, governance, replay, PCCL, or Human Interface architecture was introduced.

Regression coverage was added in `tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py` to verify that a governed bridge turn summary binds Worker invocation and replay certification from the certified continuation envelope even when the proposal-level `worker_invoked` field is false.

## Validation Results

Validation performed:

- `python -m pytest tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py tests/test_g15_runtime_06_governed_development_runtime_continuation.py` - 6 passed.
- `python -m pytest tests/` - 5890 passed, 1 skipped.
- `git diff --check` - passed.

Full-suite generated replay fixture side effects under `.runtime/aigol` were restored after validation. They were test output, not part of this implementation.

## Architectural Impact Assessment

Platform Core ownership is preserved. The Human Interface still collects input and approval, then delegates to Platform Core runtime entry.

Governance ownership is preserved. The implementation does not authorize execution in `./aicli`; it only projects certified continuation evidence that already exists.

Replay ownership is preserved. Worker and replay completion remain evidenced by existing replay artifacts.

Worker authority separation is preserved. Worker invocation continues through the existing Worker lifecycle path.

Fail-closed behavior is preserved. External provider unavailability remains recorded at the provider boundary and does not create a duplicate execution path.

## Remaining Observations

The proposal artifact remains expected to show `approval_required = true` and `worker_invoked = false`. That artifact is not the terminal runtime result.

The local runtime evidence also shows `OpenAI provider unavailable` at the external worker provider boundary. That is environment/provider availability evidence after Worker invocation was reached, not evidence that the Worker invocation binding was skipped.

## Final Recommendation

Use the certified continuation and Human Interface runtime result as the authoritative post-approval evidence for Worker invocation. Do not use the proposal capture alone to determine terminal runtime completion.

Future Human Interfaces should follow the same binding pattern: collect human interaction state, delegate approval to `run_human_interface_runtime_entry(...)`, and project Worker/replay milestones from Platform Core certified continuation evidence.

## Final Verdict

IMPLEMENTED_WITH_OBSERVATIONS
