# AIGOL_WORKER_ASSIGNMENT_TO_DISPATCH_INTEGRATION_REVIEW_V1

## Status

Review-only integration assessment.

No worker dispatch runtime was changed. No worker invocation was implemented. No execution runtime was changed. No retry behavior was implemented. No repair behavior was implemented.

## Executive Finding

`WORKER_ASSIGNMENT_ARTIFACT_V1` is compatible with the existing `WORKER_DISPATCH_ARTIFACT_V1` runtime boundary.

The existing dispatch runtime can consume worker assignment output without architectural changes because it already requires:

- the assignment artifact;
- the assignment replay reference;
- assignment hash continuity;
- worker identity continuity;
- worker invocation request lineage continuity;
- authorization and execution packet lineage continuity;
- pre-dispatch authority flags.

The runtime-level assignment-to-dispatch boundary is certified compatible.

One existing CLI acceptance smoke in `tests/test_worker_dispatch_runtime_v1.py` currently fails because the returned turn payload does not expose `worker_dispatch_status` in that path. This is a downstream CLI visibility/status propagation issue, not an artifact-boundary incompatibility between assignment and dispatch.

## Reviewed Components

Primary runtime files:

- `aigol/runtime/worker_assignment_runtime.py`
- `aigol/runtime/worker_dispatch_runtime.py`

Primary tests:

- `tests/test_worker_dispatch_runtime_v1.py`

## Assignment Output Shape

`worker_assignment_runtime._assignment_artifact(...)` produces `WORKER_ASSIGNMENT_ARTIFACT_V1` with the fields required by dispatch intake:

- `worker_assignment_id`
- `assignment_status = WORKER_ASSIGNED`
- `worker_id`
- `worker_hash`
- `worker_family`
- `worker_role`
- `worker_invocation_request_reference`
- `worker_invocation_request_hash`
- `authorization_reference`
- `authorization_hash`
- `execution_packet_reference`
- `execution_packet_hash`
- `allowed_outputs`
- `forbidden_operations`
- `validation_requirements`
- `worker_state_after = ASSIGNED`
- `canonical_chain_id`
- `replay_reference`
- `artifact_hash`

It also preserves pre-dispatch boundaries:

- `worker_assigned = True`
- `worker_dispatched = False`
- `worker_invoked = False`
- `execution_started = False`
- `result_created = False`

## Dispatch Intake Requirements

`worker_dispatch_runtime.dispatch_assigned_worker(...)` consumes:

- `worker_assignment_artifact`
- `worker_assignment_replay_reference`
- `worker_dispatch_id`
- dispatcher identity and timestamp
- dispatch replay directory

Before creating a dispatch artifact, it reconstructs assignment replay through `_load_assignment_lineage(...)`, verifies the provided assignment artifact against replay, and confirms lineage back to `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`.

## Compatibility Verification

The dispatch runtime validates that:

- assignment replay reconstructs successfully;
- assignment status is `WORKER_ASSIGNED`;
- worker state is `ASSIGNED`;
- assignment artifact hash matches the replay artifact hash;
- worker invocation request replay reconstructs;
- assignment request hash matches assignment evidence;
- authorization hash matches assignment evidence;
- execution packet hash matches assignment evidence;
- canonical chain ID matches assignment evidence;
- authority continuity remains intact.

The resulting dispatch artifact copies the required assignment-derived fields into `WORKER_DISPATCH_ARTIFACT_V1`:

- assignment reference and hash;
- worker invocation request reference and hash;
- authorization reference and hash;
- execution packet reference and hash;
- worker identity, family, and role;
- allowed outputs;
- forbidden operations;
- validation requirements;
- chain ID;
- replay reference.

## Governance Boundary

Dispatch is not invocation or execution.

`WORKER_DISPATCH_ARTIFACT_V1` marks dispatch requested/performed, but preserves:

- `worker_invoked = False`
- `execution_started = False`
- `result_created = False`
- no repair behavior
- no retry behavior
- no governance mutation
- no replay mutation

This boundary is consistent with the certified pipeline:

```text
WORKER_INVOCATION_REQUEST_ARTIFACT_V1
-> WORKER_ASSIGNMENT_ARTIFACT_V1
-> WORKER_DISPATCH_ARTIFACT_V1
-> later invocation boundary
```

## Missing Bindings

No blocking artifact-to-artifact binding is missing for the assignment-to-dispatch runtime boundary.

The dispatch runtime already binds:

- assignment artifact hash;
- assignment replay reference;
- worker invocation request lineage;
- authorization lineage;
- execution packet lineage;
- worker identity;
- chain continuity;
- replay continuity.

## Duplicate Logic

Duplicate logic found: `TRUE_NON_BLOCKING`.

Reason:

- dispatch independently revalidates assignment structure and authority flags that assignment runtime already validates;
- dispatch independently reconstructs assignment replay and worker invocation request replay;
- replay hash/wrapper verification patterns repeat across worker runtimes.

This duplication is intentional defensive governance logic and does not require architectural change.

## Required Fixes

No runtime fix is required for assignment-to-dispatch compatibility.

Non-blocking downstream issue:

- CLI acceptance smoke `test_cli_acceptance_flows_reach_worker_dispatched` currently fails with missing `worker_dispatch_status` in the returned turn payload.
- This should be handled as a later CLI status propagation/visibility cleanup if that CLI path remains canonical.
- It does not block `WORKER_ASSIGNMENT_ARTIFACT_V1` consumption by the dispatch runtime.

## Validation

Runtime boundary validation:

```text
python -m pytest tests/test_worker_dispatch_runtime_v1.py::test_worker_assigned_becomes_worker_dispatched tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_persists_replay_evidence tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_fails_closed_on_worker_identity_mismatch tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_fails_closed_on_assignment_mismatch tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_fails_closed_on_packet_mismatch tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_fails_closed_on_authority_violation tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_reconstruction_detects_replay_corruption tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_reconstruction_detects_chain_mismatch tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_runtime_preserves_authority_boundaries
```

Result:

```text
11 passed
```

Full dispatch test file status:

```text
11 passed, 1 failed
```

Failure:

```text
test_cli_acceptance_flows_reach_worker_dispatched
KeyError: worker_dispatch_status
```

## Minimal Next Milestone

```text
AIGOL_WORKER_DISPATCH_TO_INVOCATION_INTEGRATION_REVIEW_V1
```

Rationale:

The assignment-to-dispatch runtime boundary is compatible. The next architectural boundary is whether `WORKER_DISPATCH_ARTIFACT_V1` can be consumed by the existing worker invocation runtime without architectural changes.

## Final Outputs

```text
WORKER_DISPATCH_COMPATIBLE = TRUE
ARCHITECTURAL_CHANGE_REQUIRED = FALSE
DUPLICATE_LOGIC_FOUND = TRUE_NON_BLOCKING
MINIMAL_NEXT_MILESTONE = AIGOL_WORKER_DISPATCH_TO_INVOCATION_INTEGRATION_REVIEW_V1
READY_FOR_WORKER_DISPATCH = TRUE
```
