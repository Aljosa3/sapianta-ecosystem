# AIGOL_AUTHORIZATION_TO_WORKER_REQUEST_INTEGRATION_REVIEW_V1

## Status

Review-only integration certification.

No worker assignment was implemented. No worker dispatch was implemented. No worker invocation was implemented. No execution was implemented. No retry behavior was implemented. No repair behavior was implemented.

## Purpose

Review the integration boundary between:

```text
EXECUTION_AUTHORIZATION_RUNTIME
```

and:

```text
WORKER_INVOCATION_REQUEST_ARTIFACT_V1
```

after certification of:

- `AIGOL_OCS_FOUNDATION_FREEZE_V2`;
- `AIGOL_OCS_TO_EXECUTION_HANDOFF_RUNTIME_V1`;
- `AIGOL_EXECUTION_READINESS_RUNTIME_V1`;
- `AIGOL_EXECUTION_AUTHORIZATION_INTEGRATION_REVIEW_V1`.

## Reviewed Components

### Authorization Runtime

Reviewed file:

```text
aigol/runtime/execution_authorization_runtime.py
```

The authorization runtime produces:

- `EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1`.

The authorization artifact exposes worker-request-relevant fields:

- `authorization_id`;
- `authorization_status`;
- `chain_id`;
- `execution_ready_reference`;
- `execution_ready_hash`;
- `execution_candidate_reference`;
- `execution_candidate_hash`;
- `execution_packet_reference`;
- `execution_packet_hash`;
- `approval_status`;
- `approval_reference`;
- `approval_hash`;
- `authorized_scope.allowed_outputs`;
- `authorized_scope.forbidden_operations`;
- `authorized_scope.worker_role_requirements`;
- `authorization_revoked`;
- `authorization_expires_at`.

### Worker Request Runtime

Reviewed file:

```text
aigol/runtime/worker_invocation_request_runtime.py
```

Primary entrypoint:

```text
create_worker_invocation_request(...)
```

The runtime consumes:

```text
execution_authorization_replay_reference
```

and creates:

- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`.

It does not assign, dispatch, invoke, or execute a worker.

## Compatibility Finding

The existing authorization runtime produces the fields required by the worker request runtime.

Legacy compatibility is certified:

```text
legacy execution-ready replay
-> EXECUTION_AUTHORIZATION_ARTIFACT_V1
-> WORKER_INVOCATION_REQUEST_ARTIFACT_V1
```

However, OCS-readiness compatibility is not yet complete:

```text
OCS execution-ready replay
-> EXECUTION_AUTHORIZATION_ARTIFACT_V1
-> worker request runtime
```

currently has a runtime loader gap.

## Exact Gap

`execution_authorization_runtime.py` can reconstruct both legacy and OCS readiness replay:

```text
reconstruct_governed_implementation_dry_run_replay(...)
or
reconstruct_ocs_execution_readiness_replay(...)
```

`worker_invocation_request_runtime.py` still reconstructs only:

```text
reconstruct_governed_implementation_dry_run_replay(...)
```

inside:

```text
_load_execution_ready_lineage(...)
```

This means worker request creation remains compatible with legacy authorized execution packets, but not yet with authorization records created from the new OCS execution readiness runtime.

## Missing Bindings

No authorization artifact field is missing for worker-request creation.

Missing runtime binding:

```text
worker_invocation_request_runtime._load_execution_ready_lineage
must accept OCS execution readiness replay reconstruction.
```

The required fix is narrow:

```text
try reconstruct_governed_implementation_dry_run_replay(...)
except FailClosedRuntimeError:
    reconstruct_ocs_execution_readiness_replay(...)
```

This mirrors the existing authorization runtime compatibility pattern.

## Duplicate Logic Review

Duplicate logic found:

- execution-ready four-step replay loading is duplicated between authorization and worker request runtimes;
- hash verification is repeated at each runtime boundary;
- authority boundary flags are repeated across authorization and request artifacts;
- lineage checks for candidate, packet, validation, and ready artifacts are locally revalidated.

Assessment:

This duplication is non-blocking and currently governance-useful because each boundary fails closed locally. Refactoring into a shared helper is optional and should not precede the minimal OCS readiness compatibility fix.

## Required Fixes

Required for the new OCS path:

```text
AIGOL_WORKER_REQUEST_OCS_READINESS_LINEAGE_COMPATIBILITY_FIX_V1
```

Scope:

- update worker request readiness lineage reconstruction to accept OCS readiness replay;
- preserve legacy governed dry-run replay compatibility;
- preserve fail-closed behavior;
- add a regression test proving OCS readiness authorization becomes `WORKER_INVOCATION_REQUEST_CREATED`.

Not required:

- new authorization model;
- new worker request model;
- worker assignment;
- worker dispatch;
- worker invocation;
- execution;
- repair;
- retry.

## Validation

Legacy worker request compatibility was validated with:

```text
python -m pytest tests/test_worker_invocation_request_runtime_v1.py::test_execution_authorized_becomes_worker_invocation_request_created tests/test_worker_invocation_request_runtime_v1.py::test_worker_invocation_request_fails_closed_when_authorization_missing tests/test_worker_invocation_request_runtime_v1.py::test_worker_invocation_request_fails_closed_when_authorization_expired tests/test_worker_invocation_request_runtime_v1.py::test_worker_invocation_request_fails_closed_on_authority_violation tests/test_worker_invocation_request_runtime_v1.py::test_worker_invocation_request_reconstruction_detects_replay_corruption
```

Result:

```text
7 passed
```

## Certification Finding

Authorization outputs are structurally compatible with worker request creation.

The existing worker request runtime is legacy-compatible but not fully OCS-readiness-compatible until its readiness lineage loader accepts OCS readiness replay.

Architectural change is not required. A narrow compatibility fix is required before certifying the OCS-to-worker-request path end to end.

## Final Outputs

```text
WORKER_REQUEST_COMPATIBLE = PARTIAL_LEGACY_TRUE_OCS_READINESS_BLOCKED
ARCHITECTURAL_CHANGE_REQUIRED = FALSE
DUPLICATE_LOGIC_FOUND = TRUE_NON_BLOCKING
MINIMAL_NEXT_MILESTONE = AIGOL_WORKER_REQUEST_OCS_READINESS_LINEAGE_COMPATIBILITY_FIX_V1
READY_FOR_WORKER_REQUEST_RUNTIME = FALSE_PENDING_COMPATIBILITY_FIX
```
