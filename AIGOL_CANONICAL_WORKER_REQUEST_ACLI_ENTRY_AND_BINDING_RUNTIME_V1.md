# AIGOL_CANONICAL_WORKER_REQUEST_ACLI_ENTRY_AND_BINDING_RUNTIME_V1

## Status

Implementation and certification milestone.

No worker assignment changes were implemented. No worker dispatch changes were implemented. No worker invocation changes were implemented. No worker execution changes were implemented. No repair runtime was implemented. No retry runtime was implemented. No architecture redesign was implemented.

## Goal

Implement the canonical ACLI continuation path from:

```text
EXECUTION_AUTHORIZED
-> WORKER_REQUEST_CREATED
```

## Implemented Runtime Binding

The canonical conversational router now recognizes FreshDomain worker-request continuation intent and routes it to:

```text
DOMAIN_WORKER_REQUEST
```

Existing runtime bound:

```text
AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1
```

Runtime entry point:

```text
create_worker_invocation_request(...)
```

## Supported Operator Prompts

```text
Create worker request for FreshDomain.
Continue FreshDomain to worker request.
Create authorized worker request for FreshDomain.
```

These prompts no longer route to provider fallback or OCS cognition.

## Replay Binding

The new binding helper:

```text
find_latest_domain_execution_authorization(...)
```

locates the latest unconsumed domain execution authorization by:

- scanning session replay for `execution_authorization` turns;
- reconstructing `EXECUTION_AUTHORIZED` replay;
- correlating the authorization request to a domain execution-ready bridge by replay reference or replay hash;
- matching the approved domain identity from the bridge;
- rejecting authorizations that already have a worker invocation request replay.

The resulting authorization replay reference is passed to the existing worker request runtime.

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
```

The worker request turn records:

- `worker_request_created = true`
- `worker_assigned = false`
- `worker_dispatched = false`
- `worker_invoked = false`
- `execution_started = false`
- `domain_created = false`

## Governance Preservation

Replay continuity is preserved by binding from the worker request replay back to the execution authorization replay.

Fail-closed behavior is preserved:

- missing execution authorization replay fails closed;
- domain mismatch fails closed by absence of a matching authorization;
- duplicate worker request creation is blocked by excluding already-consumed execution authorization replay;
- corrupt authorization replay is ignored and cannot authorize request creation.

Authority boundaries are preserved:

- the worker request runtime creates no worker assignment;
- no worker is dispatched;
- no worker is invoked;
- no worker execution starts;
- no repair or retry behavior is introduced.

## Regression Coverage

Added coverage for:

- canonical router recognition of all worker-request prompts;
- worker-request intent detection;
- latest execution authorization replay binding;
- already-requested authorization exclusion;
- full FreshDomain ACLI progression to `WORKER_INVOCATION_REQUEST_CREATED`;
- no assignment, dispatch, invocation, execution, or domain creation from this milestone.

## Validation

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py tests/test_worker_invocation_request_runtime_v1.py::test_execution_authorized_becomes_worker_invocation_request_created tests/test_worker_invocation_request_runtime_v1.py::test_worker_invocation_request_runtime_preserves_authority_boundaries
```

Result:

```text
66 passed
```

## Final Outputs

```text
CANONICAL_WORKER_REQUEST_ACLI_ENTRY_REGISTERED = TRUE
WORKER_REQUEST_CREATED = TRUE
REPLAY_CONTINUITY_PRESERVED = TRUE
FAIL_CLOSED_PRESERVED = TRUE
READY_FOR_REAL_WORKER_ASSIGNMENT_ACCEPTANCE = TRUE
```
