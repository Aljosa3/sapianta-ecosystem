# AIGOL_CANONICAL_WORKER_ASSIGNMENT_ACLI_ENTRY_AND_BINDING_RUNTIME_V1

## Status

Implementation and certification milestone.

No dispatch changes were implemented. No invocation changes were implemented. No execution changes were implemented. No repair runtime was implemented. No retry runtime was implemented. No architecture redesign was implemented.

## Goal

Implement the canonical ACLI continuation path from:

```text
WORKER_INVOCATION_REQUEST_CREATED
-> WORKER_ASSIGNED
```

## Implemented Runtime Binding

The canonical conversational router now recognizes FreshDomain worker-assignment continuation intent and routes it to:

```text
DOMAIN_WORKER_ASSIGNMENT
```

Existing runtime bound:

```text
AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1
```

Runtime entry point:

```text
assign_worker_from_invocation_request(...)
```

## Supported Operator Prompts

```text
Assign worker for FreshDomain.
Continue FreshDomain to worker assignment.
Create worker assignment for FreshDomain.
```

These prompts no longer route to provider fallback or OCS cognition.

## Replay Binding

The new binding helper:

```text
find_latest_domain_worker_invocation_request(...)
```

locates the latest unassigned domain worker invocation request by:

- scanning session replay for `worker_invocation_request` turns;
- reconstructing `WORKER_INVOCATION_REQUEST_CREATED` replay;
- following the request's authorization replay reference;
- correlating the authorization request to a domain execution-ready bridge by replay reference or replay hash;
- matching the approved domain identity from the bridge;
- rejecting invocation requests that already have a worker assignment replay.

The resulting worker invocation request artifact and replay reference are passed to the existing worker assignment runtime.

## ACLI Continuation

The interactive ACLI now supports:

```text
Create Domain
-> Clarification Required
-> Clarification Reply
-> Clarification Resolved
-> Handoff Review
-> WORKER_BINDING_APPROVED
-> DOMAIN_APPROVAL_BOUND
-> DOMAIN_EXECUTION_READY_BRIDGED
-> EXECUTION_READY
-> EXECUTION_AUTHORIZED
-> WORKER_INVOCATION_REQUEST_CREATED
-> WORKER_ASSIGNED
```

The worker assignment turn records:

- `worker_assigned = true`
- `worker_dispatched = false`
- `worker_invoked = false`
- `execution_started = false`
- `domain_created = false`

## Governance Preservation

Replay continuity is preserved by binding assignment replay to the worker invocation request replay, which itself binds to execution authorization and execution-ready bridge lineage.

Fail-closed behavior is preserved:

- missing worker invocation request replay fails closed;
- domain mismatch fails closed by absence of a matching request;
- duplicate worker assignment is blocked by excluding already-assigned request replay;
- corrupt request or authorization lineage cannot produce assignment.

Authority boundaries are preserved:

- assignment does not dispatch a worker;
- assignment does not invoke a worker;
- assignment does not execute work;
- no repair or retry behavior is introduced.

## Regression Coverage

Added coverage for:

- canonical router recognition of all worker-assignment prompts;
- worker-assignment intent detection;
- latest worker invocation request replay binding;
- already-assigned request exclusion;
- full FreshDomain ACLI progression to `WORKER_ASSIGNED`;
- no dispatch, invocation, execution, or domain creation from this milestone.

## Validation

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py tests/test_worker_assignment_runtime_v1.py::test_worker_invocation_request_becomes_worker_assigned tests/test_worker_assignment_runtime_v1.py::test_worker_assignment_runtime_preserves_authority_boundaries
```

Result:

```text
72 passed
```

## Final Outputs

```text
CANONICAL_WORKER_ASSIGNMENT_ACLI_ENTRY_REGISTERED = TRUE
WORKER_ASSIGNED = TRUE
REPLAY_CONTINUITY_PRESERVED = TRUE
FAIL_CLOSED_PRESERVED = TRUE
READY_FOR_REAL_WORKER_DISPATCH_ACCEPTANCE = TRUE
```
