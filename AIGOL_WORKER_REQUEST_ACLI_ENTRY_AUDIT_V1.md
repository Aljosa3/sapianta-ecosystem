# AIGOL_WORKER_REQUEST_ACLI_ENTRY_AUDIT_V1

## Status

Audit and certification artifact.

No worker execution was implemented. No worker changes were implemented. No dispatch changes were implemented. No authorization changes were implemented. No architecture redesign was implemented.

## Goal

Determine the canonical continuation path from:

```text
EXECUTION_AUTHORIZED
-> WORKER_REQUEST_CREATED
```

for the FreshDomain ACLI workflow.

## Context

FreshDomain reached execution authorization through ACLI:

```text
DOMAIN_EXECUTION_READY_BRIDGED
-> EXECUTION_READY
-> EXECUTION_AUTHORIZED
```

Observed result:

```text
Authorization Status: EXECUTION_AUTHORIZED
Authorization Reference:
AIGOL-INTERACTIVE-CONVERSATION-000001:TURN-000204:EXECUTION-AUTHORIZATION
```

No Worker was assigned, dispatched, invoked, or executed.

## Runtime Located

The next certified direct runtime after execution authorization is:

```text
AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1
```

Runtime entry point:

```text
aigol/runtime/worker_invocation_request_runtime.py
create_worker_invocation_request(...)
```

It consumes:

- `execution_authorization_replay_reference`
- `invocation_request_id`
- `requested_by`
- `requested_at`
- `replay_dir`

It reconstructs the execution authorization replay and requires:

```text
authorization_status = EXECUTION_AUTHORIZED
```

It produces:

```text
WORKER_INVOCATION_REQUEST_CREATED
WORKER_INVOCATION_REQUEST_ARTIFACT_V1
WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1
```

It does not assign, dispatch, invoke, execute, validate results, repair, retry, or terminate.

## Direct Worker Lifecycle Continuation

The direct runtime chain exists:

```text
EXECUTION_AUTHORIZED
-> create_worker_invocation_request(...)
-> WORKER_INVOCATION_REQUEST_CREATED
-> assign_worker_from_invocation_request(...)
-> WORKER_ASSIGNED
-> dispatch_assigned_worker(...)
-> WORKER_DISPATCHED
-> invoke_dispatched_worker(...)
-> WORKER_INVOKED
```

Direct runtime validation passed for worker request, assignment, dispatch, and invocation.

## ACLI Routing Audit

The canonical conversational registry currently includes:

- `AUTHORIZED_DOMAIN_ARTIFACT_REQUEST_REVIEW`
- `DOMAIN_EXECUTION_READY_AUTHORIZATION_BRIDGE`
- `DOMAIN_EXECUTION_AUTHORIZATION`

It does not include a FreshDomain worker-request continuation workflow.

Router probe results:

```text
Create worker request for FreshDomain.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Create worker invocation request for FreshDomain.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Continue FreshDomain to worker request.
-> OCS_LLM_COGNITION

Request worker for FreshDomain.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Create worker invocation request from FreshDomain execution authorization.
-> DEFAULT_PROVIDER_ASSISTED_CONVERSATION

Continue FreshDomain to worker assignment.
-> OCS_LLM_COGNITION
```

Therefore the worker request runtime is directly reachable as a certified runtime, but not reachable from the canonical FreshDomain ACLI continuation path after `EXECUTION_AUTHORIZED`.

## Existing Non-FreshDomain Paths

Older implementation/development ACLI paths can internally proceed from authorization into worker request, assignment, dispatch, and invocation.

Those paths do not establish a canonical FreshDomain continuation from:

```text
DOMAIN_EXECUTION_AUTHORIZATION
-> EXECUTION_AUTHORIZED
```

to:

```text
WORKER_INVOCATION_REQUEST_CREATED
```

The FreshDomain execution authorization ACLI branch intentionally stops after rendering the execution authorization summary and records no worker request.

## Expected Operator Prompt

No canonical FreshDomain worker-request prompt currently exists.

Recommended future canonical prompt family:

```text
Create worker invocation request for FreshDomain.
Continue FreshDomain to worker request.
Create worker request from FreshDomain execution authorization.
```

These prompts are not currently routed to the worker invocation request runtime.

## Blocking Component

The next blocking component is:

```text
CANONICAL_WORKER_REQUEST_ACLI_ENTRY_AND_REPLAY_BINDING
```

Required minimal behavior:

- detect FreshDomain worker-request continuation intent;
- locate the latest unconsumed `EXECUTION_AUTHORIZED` replay for the reviewed domain;
- bind that replay to `create_worker_invocation_request(...)`;
- produce `WORKER_INVOCATION_REQUEST_CREATED`;
- preserve replay continuity and authority boundaries;
- stop before assignment, dispatch, invocation, execution, repair, and retry unless separately authorized by later milestones.

## Certification

This audit certifies:

- worker request runtime location;
- worker request direct runtime capability;
- worker assignment direct runtime capability;
- worker dispatch direct runtime capability;
- worker invocation direct runtime capability;
- absence of canonical FreshDomain ACLI worker-request routing;
- next blocking component.

This audit does not certify:

- new ACLI routing;
- worker request creation from FreshDomain ACLI;
- worker assignment from FreshDomain ACLI;
- worker dispatch from FreshDomain ACLI;
- worker invocation from FreshDomain ACLI;
- worker execution.

## Validation

```text
python -m pytest tests/test_worker_invocation_request_runtime_v1.py::test_execution_authorized_becomes_worker_invocation_request_created tests/test_worker_assignment_runtime_v1.py::test_worker_invocation_request_becomes_worker_assigned tests/test_worker_dispatch_runtime_v1.py::test_worker_assigned_becomes_worker_dispatched tests/test_worker_invocation_runtime_v1.py::test_worker_dispatched_becomes_worker_invoked
```

Result:

```text
12 passed
```

## Final Outputs

```text
WORKER_REQUEST_RUNTIME_LOCATED = TRUE
EXPECTED_OPERATOR_PROMPT = NONE_CURRENTLY_REGISTERED_FOR_FRESHDOMAIN_WORKER_REQUEST
WORKER_REQUEST_CREATED_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
WORKER_ASSIGNMENT_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
WORKER_INVOCATION_REACHABLE = TRUE_DIRECT_RUNTIME_FALSE_CANONICAL_FRESHDOMAIN_ACLI
NEXT_BLOCKING_COMPONENT = CANONICAL_WORKER_REQUEST_ACLI_ENTRY_AND_REPLAY_BINDING
READY_FOR_REAL_WORKER_REQUEST_ACCEPTANCE = FALSE
```
