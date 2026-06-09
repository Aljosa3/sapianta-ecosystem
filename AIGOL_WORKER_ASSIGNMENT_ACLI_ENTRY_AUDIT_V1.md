# AIGOL_WORKER_ASSIGNMENT_ACLI_ENTRY_AUDIT_V1

## Status

Audit and certification artifact.

No worker execution was implemented. No worker behavior changes were implemented. No dispatch changes were implemented. No architecture redesign was implemented.

## Goal

Determine the canonical ACLI continuation path from:

```text
WORKER_INVOCATION_REQUEST_CREATED
-> WORKER_ASSIGNED
```

## Context

FreshDomain successfully reached:

```text
WORKER_INVOCATION_REQUEST_CREATED
```

Observed output:

```text
Request Status: WORKER_INVOCATION_REQUEST_CREATED

Invocation Request Reference:
AIGOL-INTERACTIVE-CONVERSATION-000001:TURN-000205:WORKER-INVOCATION-REQUEST

No Worker has been assigned, dispatched, invoked, or executed.
```

## Runtime Located

The next certified direct runtime after worker invocation request creation is:

```text
AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1
```

Runtime entry point:

```text
aigol/runtime/worker_assignment_runtime.py
assign_worker_from_invocation_request(...)
```

It consumes:

- `worker_invocation_request_artifact`
- `worker_invocation_request_replay_reference`
- `worker_registry_artifacts`
- `worker_assignment_id`
- `assigned_by`
- `assigned_at`
- `replay_dir`

It requires:

```text
request_status = WORKER_INVOCATION_REQUEST_CREATED
```

It produces:

```text
WORKER_ASSIGNED
WORKER_ASSIGNMENT_ARTIFACT_V1
WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1
```

It does not dispatch, invoke, execute, validate results, repair, retry, or terminate.

## Direct Lifecycle Continuation

The direct runtime chain exists:

```text
WORKER_INVOCATION_REQUEST_CREATED
-> assign_worker_from_invocation_request(...)
-> WORKER_ASSIGNED
-> dispatch_assigned_worker(...)
-> WORKER_DISPATCHED
-> invoke_dispatched_worker(...)
-> WORKER_INVOKED
```

Direct runtime validation passed for assignment, dispatch, and invocation.

## ACLI Routing Audit

The canonical FreshDomain conversational registry currently includes:

- `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW`
- `DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE`
- `DOMAIN_EXECUTION_AUTHORIZATION`
- `DOMAIN_WORKER_REQUEST`

It does not include a FreshDomain worker-assignment continuation workflow.

Router probe results:

```text
Assign worker for FreshDomain.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Assign FreshDomain worker.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Continue FreshDomain to worker assignment.
-> OCS_LLM_COGNITION

Create worker assignment for FreshDomain.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Assign worker from FreshDomain worker request.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Continue FreshDomain worker request to assignment.
-> OCS_LLM_COGNITION
```

Therefore worker assignment is directly reachable as a certified runtime, but not reachable from the canonical FreshDomain ACLI continuation path after `WORKER_INVOCATION_REQUEST_CREATED`.

## Expected Operator Prompt

No canonical FreshDomain worker-assignment prompt currently exists.

Recommended future canonical prompt family:

```text
Assign worker for FreshDomain.
Continue FreshDomain to worker assignment.
Assign worker from FreshDomain worker request.
```

These prompts are not currently routed to the worker assignment runtime.

## Blocking Component

The next blocking component is:

```text
CANONICAL_WORKER_ASSIGNMENT_ACLI_ENTRY_AND_REPLAY_BINDING
```

Required minimal behavior:

- detect FreshDomain worker-assignment continuation intent;
- locate the latest unconsumed `WORKER_INVOCATION_REQUEST_CREATED` replay for the reviewed domain;
- bind that replay to `assign_worker_from_invocation_request(...)`;
- use registered worker evidence or the existing deterministic default worker registry helper;
- produce `WORKER_ASSIGNED`;
- preserve replay continuity and authority boundaries;
- stop before dispatch, invocation, execution, result validation, repair, and retry unless separately authorized by later milestones.

## Certification

This audit certifies:

- worker assignment runtime location;
- worker assignment direct runtime capability;
- worker dispatch direct runtime capability;
- worker invocation direct runtime capability;
- absence of canonical FreshDomain ACLI worker-assignment routing;
- next blocking component.

This audit does not certify:

- new ACLI routing;
- worker assignment from FreshDomain ACLI;
- worker dispatch from FreshDomain ACLI;
- worker invocation from FreshDomain ACLI;
- worker execution.

## Validation

```text
python -m pytest tests/test_worker_assignment_runtime_v1.py::test_worker_invocation_request_becomes_worker_assigned tests/test_worker_dispatch_runtime_v1.py::test_worker_assigned_becomes_worker_dispatched tests/test_worker_invocation_runtime_v1.py::test_worker_dispatched_becomes_worker_invoked
```

Result:

```text
9 passed
```

## Final Outputs

```text
WORKER_ASSIGNMENT_RUNTIME_LOCATED = TRUE
EXPECTED_OPERATOR_PROMPT = NONE_CURRENTLY_REGISTERED_FOR_FRESHDOMAIN_WORKER_ASSIGNMENT
WORKER_ASSIGNED_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
WORKER_DISPATCH_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
WORKER_INVOCATION_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
NEXT_BLOCKING_COMPONENT = CANONICAL_WORKER_ASSIGNMENT_ACLI_ENTRY_AND_REPLAY_BINDING
READY_FOR_REAL_WORKER_ASSIGNMENT_ACCEPTANCE = FALSE
```
