# AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_V1

## Status

Certified bounded Worker invocation request preparation runtime.

## Final Classification

```text
AIGOL_WORKER_INVOCATION_REQUEST_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Transform a replay-valid `EXECUTION_AUTHORIZED` artifact into
`WORKER_INVOCATION_REQUEST_CREATED` without assigning, dispatching, invoking, or
executing any Worker.

## Lifecycle

```text
IMPLEMENTATION_HANDOFF_CREATED
-> EXECUTION_READY
-> EXECUTION_AUTHORIZED
-> WORKER_INVOCATION_REQUEST_CREATED
```

## Input

The runtime consumes the replay reference for
`EXECUTION_AUTHORIZATION_ARTIFACT_V1`.

It reconstructs authorization replay and then reconstructs the referenced
execution-ready replay before producing a request.

## Output Artifacts

The runtime persists:

- `WORKER_INVOCATION_REQUEST_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- `WORKER_INVOCATION_REQUEST_RESULT_ARTIFACT_V1`.

## Invocation Request Model

`WORKER_INVOCATION_REQUEST_ARTIFACT_V1` contains:

- chain id;
- authorization reference and hash;
- execution packet reference and hash;
- Worker role;
- target Worker family;
- allowed outputs;
- forbidden operations;
- validation requirements;
- replay references;
- request hash.

The request is non-authoritative. It prepares the next lifecycle boundary but
does not select, dispatch, invoke, execute, or complete a Worker.

## Validation

The runtime verifies:

- authorization lineage;
- packet lineage;
- candidate lineage;
- handoff lineage;
- approval lineage;
- chain continuity;
- replay continuity;
- authority continuity;
- authorization expiry;
- artifact and wrapper hash continuity.

## Fail-Closed Conditions

The runtime fails closed when:

- authorization replay is missing;
- authorization is invalid;
- authorization is expired;
- chain continuity breaks;
- replay is corrupt;
- packet lineage is corrupt;
- authority continuity is violated;
- request scope is ambiguous.

## Authority Boundaries

This runtime may:

- create invocation request evidence;
- classify invocation request scope;
- create the invocation request artifact;
- record the invocation request result.

This runtime may not:

- assign Workers;
- dispatch Workers;
- invoke Workers;
- execute Workers;
- create results;
- create approvals;
- modify governance;
- mutate existing replay.

## Replay Model

Replay is append-only and records:

```text
invocation_request_evidence_recorded
-> invocation_request_classification_recorded
-> invocation_request_artifact_recorded
-> invocation_request_result_recorded
```

Replay reconstruction verifies:

- lineage continuity;
- authority continuity;
- replay continuity;
- hash continuity;
- request hash continuity.

## CLI Before And After

Before:

```text
Execution Authorization
Authorization Status: EXECUTION_AUTHORIZED
No Worker has been assigned, dispatched, invoked, or executed.
```

After:

```text
Execution Authorization
Authorization Status: EXECUTION_AUTHORIZED
No Worker has been assigned, dispatched, invoked, or executed.

Worker Invocation Request
Request Status: WORKER_INVOCATION_REQUEST_CREATED
No Worker has been assigned, dispatched, invoked, or executed.
```

## Acceptance Results

| Scenario | Result |
| --- | --- |
| Filesystem Worker | `IMPLEMENTATION_HANDOFF_CREATED -> EXECUTION_READY -> EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED` |
| Monitoring Worker | `IMPLEMENTATION_HANDOFF_CREATED -> EXECUTION_READY -> EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED` |
| Trading Improvement | `Approve -> IMPLEMENTATION_HANDOFF_CREATED -> EXECUTION_READY -> EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED` |

## Remaining Gap Before First Worker Assignment

The next missing binding is assignment consumption of
`WORKER_INVOCATION_REQUEST_ARTIFACT_V1`.

Before first Worker assignment, AiGOL still needs a governed assignment runtime
that validates:

- invocation request lineage;
- registered Worker identity;
- Worker role compatibility;
- target Worker family compatibility;
- allowed-output scope;
- forbidden-operation scope;
- replay continuity;
- authority continuity.
