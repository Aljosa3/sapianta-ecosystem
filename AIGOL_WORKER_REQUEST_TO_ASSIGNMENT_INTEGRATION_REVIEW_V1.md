# AIGOL_WORKER_REQUEST_TO_ASSIGNMENT_INTEGRATION_REVIEW_V1

## Status

Review-only integration certification.

No worker dispatch was implemented. No worker invocation was implemented. No execution was implemented. No retry behavior was implemented. No repair behavior was implemented.

## Purpose

Review the integration boundary between:

```text
WORKER_INVOCATION_REQUEST_ARTIFACT_V1
```

and:

```text
WORKER_ASSIGNMENT_ARTIFACT_V1
```

after certification of:

- `AIGOL_OCS_FOUNDATION_FREEZE_V2`;
- `AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1`;
- `AIGOL_EXECUTION_READINESS_RUNTIME_V1`;
- `AIGOL_WORKER_REQUEST_OCS_READINESS_LINEAGE_COMPATIBILITY_FIX_V1`.

## Reviewed Components

### Worker Request Runtime

Reviewed file:

```text
aigol/runtime/worker_invocation_request_runtime.py
```

The worker request runtime produces:

- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`.

The canonical request artifact exposes assignment-relevant fields:

- `worker_invocation_request_id`;
- `request_status`;
- `chain_id`;
- `authorization_reference`;
- `authorization_hash`;
- `execution_packet_reference`;
- `execution_packet_hash`;
- `worker_role`;
- `target_worker_family`;
- `allowed_outputs`;
- `forbidden_operations`;
- `validation_requirements`;
- `replay_references`;
- `request_hash`;
- pre-assignment boundary flags.

### Worker Assignment Runtime

Reviewed file:

```text
aigol/runtime/worker_assignment_runtime.py
```

Primary entrypoint:

```text
assign_worker_from_invocation_request(...)
```

The runtime consumes:

- `worker_invocation_request_artifact`;
- `worker_invocation_request_replay_reference`;
- `worker_registry_artifacts`;
- assignment actor and timestamp.

It creates:

- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`.

It does not dispatch, invoke, execute, repair, or retry.

## Compatibility Finding

Worker request outputs can be consumed by the existing worker assignment runtime without architectural changes.

The boundary works because the assignment runtime validates:

- request artifact hash;
- request replay reconstruction;
- `request_status = WORKER_INVOCATION_REQUEST_CREATED`;
- `request_hash`;
- authorization reference and hash;
- execution packet reference and hash;
- worker role;
- target worker family;
- allowed outputs;
- forbidden operations;
- replay references;
- pre-assignment authority flags.

The assignment runtime then selects exactly one compatible registered worker and creates `WORKER_ASSIGNMENT_ARTIFACT_V1`.

## Required Worker Registry Binding

Assignment requires registered worker evidence.

Current runtime support:

```text
default_worker_registry_for_request(...)
```

provides deterministic in-memory worker registry evidence for CLI continuity and tests.

This is sufficient for the current assignment boundary. A future production worker registry review may replace or extend registry sourcing, but it is not required for compatibility between request and assignment artifacts.

## Missing Bindings

No runtime-blocking binding is missing at the worker request to assignment boundary.

Non-blocking future refinement:

- formalize persistent worker registry source if assignment must move beyond deterministic in-memory registry evidence.

## Duplicate Logic Review

Duplicate logic found:

- request hash validation is performed in both request and assignment runtimes;
- replay wrapper hash checks are repeated at every runtime boundary;
- authority boundary flags are repeated across request and assignment artifacts;
- lineage checks are locally repeated in reconstruction and intake validation.

Assessment:

This duplication is non-blocking and governance-useful because assignment performs local fail-closed verification before selecting a worker.

## Required Fixes

No required runtime fix is needed for this integration boundary.

The minimal next milestone is downstream:

```text
AIGOL_WORKER_ASSIGNMENT_TO_DISPATCH_INTEGRATION_REVIEW_V1
```

## Validation

Command:

```text
python -m pytest tests/test_worker_assignment_runtime_v1.py::test_worker_invocation_request_becomes_worker_assigned tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_persists_replay_evidence tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_fails_closed_when_no_worker_exists tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_fails_closed_on_worker_family_mismatch tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_fails_closed_on_worker_role_mismatch tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_fails_closed_on_packet_mismatch tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_fails_closed_on_authority_violation tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_reconstruction_detects_replay_corruption tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_runtime_preserves_authority_boundaries
```

Result:

```text
11 passed
```

## Certification Finding

Worker request to worker assignment integration is compatible.

Architectural change is not required.

The system is ready for the worker assignment runtime boundary.

## Final Outputs

```text
WORKER_ASSIGNMENT_COMPATIBLE = TRUE
ARCHITECTURAL_CHANGE_REQUIRED = FALSE
DUPLICATE_LOGIC_FOUND = TRUE_NON_BLOCKING
MINIMAL_NEXT_MILESTONE = AIGOL_WORKER_ASSIGNMENT_TO_DISPATCH_INTEGRATION_REVIEW_V1
READY_FOR_WORKER_ASSIGNMENT = TRUE
```
