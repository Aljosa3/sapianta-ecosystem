# AIGOL_CANONICAL_WORKER_INVOCATION_ACLI_ENTRY_AND_BINDING_RUNTIME_V1

## Status

Implementation and certification milestone.

No worker execution changes were implemented. No result capture changes were implemented. No repair runtime was implemented. No retry runtime was implemented. No architecture redesign was implemented.

## Goal

Implement the canonical ACLI continuation path from:

```text
WORKER_DISPATCHED
-> WORKER_INVOKED
```

## Implemented Runtime Binding

The canonical conversational router now recognizes FreshDomain worker-invocation continuation intent and routes it to:

```text
DOMAIN_WORKER_INVOCATION
```

Existing runtime bound:

```text
AIGOL_WORKER_INVOCATION_RUNTIME_V1
```

Runtime entry point:

```text
invoke_dispatched_worker(...)
```

## Supported Operator Prompts

```text
Invoke worker for FreshDomain.
Continue FreshDomain to worker invocation.
Create worker invocation for FreshDomain.
```

These prompts no longer route to provider fallback or OCS cognition.

## Replay Binding

The new binding helper:

```text
find_latest_domain_worker_dispatch(...)
```

locates the latest uninvoked domain worker dispatch by:

- scanning session replay for `worker_dispatch` turns;
- reconstructing `WORKER_DISPATCHED` replay;
- following dispatch evidence to worker assignment replay;
- following assignment evidence to worker invocation request replay;
- following the request authorization replay reference;
- correlating the authorization request to a domain execution-ready bridge by replay reference or replay hash;
- matching the approved domain identity from the bridge;
- rejecting dispatches that already have worker invocation replay.

The resulting worker dispatch artifact and replay reference are passed to the existing worker invocation runtime.

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
-> WORKER_INVOKED
```

The worker invocation turn records:

- `worker_assigned = true`
- `worker_dispatched = true`
- `worker_invoked = true`
- `execution_started = false`
- `domain_created = false`

## Governance Preservation

Replay continuity is preserved by binding invocation replay to worker dispatch replay, which itself binds to assignment, request, authorization, and execution-ready bridge lineage.

Fail-closed behavior is preserved:

- missing worker dispatch replay fails closed;
- domain mismatch fails closed by absence of a matching dispatch;
- duplicate worker invocation is blocked by excluding already-invoked dispatch replay;
- corrupt dispatch, assignment, request, or authorization lineage cannot produce invocation.

Authority boundaries are preserved:

- invocation does not execute worker output;
- invocation does not capture or validate results;
- invocation does not perform post-execution replay review;
- invocation does not terminate the chain;
- no repair or retry behavior is introduced.

## Regression Coverage

Added coverage for:

- canonical router recognition of all worker-invocation prompts;
- worker-invocation intent detection;
- latest worker dispatch replay binding;
- already-invoked dispatch exclusion;
- full FreshDomain ACLI progression to `WORKER_INVOKED`;
- no execution, result creation, replay review, termination, repair, or retry from this milestone.

## Validation

```text
python -m pytest tests/test_conversational_cli_runtime_v1.py tests/test_domain_approval_entry_to_execution_ready_authorization_bridge_runtime_v1.py tests/test_worker_invocation_runtime_v1.py::test_worker_dispatched_becomes_worker_invoked tests/test_worker_invocation_runtime_v1.py::test_worker_invocation_runtime_does_not_validate_results_or_terminate
```

Result:

```text
84 passed
```

Additional validation:

```text
python -m json.tool AIGOL_CANONICAL_WORKER_INVOCATION_ACLI_ENTRY_AND_BINDING_RUNTIME_ACCEPTANCE_EVIDENCE.json
python -m json.tool AIGOL_CANONICAL_WORKER_INVOCATION_ACLI_ENTRY_AND_BINDING_RUNTIME_CERTIFICATION.json
git diff --check
```

## Final Outputs

```text
CANONICAL_WORKER_INVOCATION_ACLI_ENTRY_REGISTERED = TRUE
WORKER_INVOKED = TRUE
REPLAY_CONTINUITY_PRESERVED = TRUE
FAIL_CLOSED_PRESERVED = TRUE
READY_FOR_REAL_WORKER_EXECUTION_ACCEPTANCE = TRUE
```
