# AIGOL_CANONICAL_WORKER_DISPATCH_ACLI_ENTRY_AND_BINDING_RUNTIME_V1

## Status

Implementation and certification milestone.

No invocation changes were implemented. No execution changes were implemented. No repair runtime was implemented. No retry runtime was implemented. No architecture redesign was implemented.

## Goal

Implement the canonical ACLI continuation path from:

```text
WORKER_ASSIGNED
-> WORKER_DISPATCHED
```

## Implemented Runtime Binding

The canonical conversational router now recognizes FreshDomain worker-dispatch continuation intent and routes it to:

```text
DOMAIN_WORKER_DISPATCH
```

Existing runtime bound:

```text
AIGOL_WORKER_DISPATCH_RUNTIME_V1
```

Runtime entry point:

```text
dispatch_assigned_worker(...)
```

## Supported Operator Prompts

```text
Dispatch worker for FreshDomain.
Continue FreshDomain to worker dispatch.
Create worker dispatch for FreshDomain.
```

These prompts no longer route to provider fallback or OCS cognition.

## Replay Binding

The new binding helper:

```text
find_latest_domain_worker_assignment(...)
```

locates the latest undispatched domain worker assignment by:

- scanning session replay for `worker_assignment` turns;
- reconstructing `WORKER_ASSIGNED` replay;
- following assignment evidence to the worker invocation request replay;
- following the request authorization replay reference;
- correlating the authorization request to a domain execution-ready bridge by replay reference or replay hash;
- matching the approved domain identity from the bridge;
- rejecting assignments that already have a worker dispatch replay.

The resulting worker assignment artifact and replay reference are passed to the existing worker dispatch runtime.

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
-> WORKER_DISPATCHED
```

The worker dispatch turn records:

- `worker_assigned = true`
- `worker_dispatched = true`
- `worker_invoked = false`
- `execution_started = false`
- `domain_created = false`

## Governance Preservation

Replay continuity is preserved by binding dispatch replay to worker assignment replay, which itself binds to request, authorization, and execution-ready bridge lineage.

Fail-closed behavior is preserved:

- missing worker assignment replay fails closed;
- domain mismatch fails closed by absence of a matching assignment;
- duplicate worker dispatch is blocked by excluding already-dispatched assignment replay;
- corrupt assignment, request, or authorization lineage cannot produce dispatch.

Authority boundaries are preserved:

- dispatch does not invoke a worker;
- dispatch does not execute work;
- dispatch does not validate results or terminate;
- no repair or retry behavior is introduced.

## Regression Coverage

Added coverage for:

- canonical router recognition of all worker-dispatch prompts;
- worker-dispatch intent detection;
- latest worker assignment replay binding;
- already-dispatched assignment exclusion;
- full FreshDomain ACLI progression to `WORKER_DISPATCHED`;
- no invocation, execution, result creation, repair, or retry from this milestone.

## Validation

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py tests/test_worker_dispatch_runtime_v1.py::test_worker_assigned_becomes_worker_dispatched tests/test_worker_dispatch_runtime_v1.py::test_worker_dispatch_runtime_preserves_authority_boundaries
```

Result:

```text
78 passed
```

## Final Outputs

```text
CANONICAL_WORKER_DISPATCH_ACLI_ENTRY_REGISTERED = TRUE
WORKER_DISPATCHED = TRUE
REPLAY_CONTINUITY_PRESERVED = TRUE
FAIL_CLOSED_PRESERVED = TRUE
READY_FOR_REAL_WORKER_INVOCATION_ACCEPTANCE = TRUE
```
