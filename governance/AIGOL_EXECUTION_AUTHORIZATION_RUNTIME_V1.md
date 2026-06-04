# AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_V1

## Status

Certified bounded execution authorization runtime.

## Final Classification

```text
AIGOL_EXECUTION_AUTHORIZATION_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Transform a replay-valid `EXECUTION_READY` packet into bounded
`EXECUTION_AUTHORIZED` evidence without assigning, dispatching, invoking, or
executing a Worker.

## Lifecycle

```text
IMPLEMENTATION_HANDOFF_CREATED
-> EXECUTION_READY
-> EXECUTION_AUTHORIZATION_REQUEST
-> EXECUTION_AUTHORIZATION_DECISION
-> EXECUTION_AUTHORIZATION_ARTIFACT
-> EXECUTION_AUTHORIZED
```

## Input

The authoritative input is the replay reference containing
`EXECUTION_READY_STATUS_ARTIFACT_V1`.

The runtime reconstructs the replay rather than trusting a detached status
artifact. This permits deterministic verification of:

- execution packet lineage;
- execution candidate lineage;
- handoff lineage;
- approval lineage;
- chain continuity;
- replay continuity;
- authority continuity;
- hash integrity.

## Output Artifacts

The runtime persists:

- `EXECUTION_AUTHORIZATION_REQUEST_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_DECISION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_ARTIFACT_V1`;
- `EXECUTION_AUTHORIZATION_RESULT_ARTIFACT_V1`.

## Authorization Model

`EXECUTION_AUTHORIZATION_ARTIFACT_V1` contains:

- authorization id and status;
- chain id;
- execution-ready, candidate, and packet references and hashes;
- approval status, reference, and hash;
- authorized outputs;
- forbidden operations;
- Worker role requirements;
- authorizing actor;
- authorization timestamp and expiry;
- revocation, transferability, and recursion flags;
- authorization hash and artifact hash.

The authorized scope is exactly the execution packet scope. Authorization cannot
expand outputs, remove forbidden operations, or change Worker role requirements.

## Approval Handling

The runtime supports:

- `APPROVAL_NOT_REQUIRED_FOR_HANDOFF` when the upstream governance decision is
  present and replay-valid;
- `APPROVED` when a valid human approval reference is present and replay-valid.

The runtime does not create approvals or treat missing approval lineage as
authorization.

## Authority Boundaries

Authorization may:

- authorize one bounded execution packet.

Authorization may not:

- assign a Worker;
- dispatch a Worker;
- invoke a Worker;
- start execution;
- create results;
- create approvals;
- modify governance;
- mutate existing replay.

## Replay Model

Replay is append-only and records:

```text
authorization_request_recorded
-> authorization_decision_recorded
-> authorization_artifact_recorded
-> authorization_result_recorded
```

Replay reconstruction verifies:

- artifact ordering;
- request lineage;
- decision lineage;
- authorization lineage;
- packet lineage;
- approval continuity;
- chain continuity;
- replay continuity;
- wrapper and artifact hash integrity.

Replay records authorization evidence. Replay does not authorize execution.

## Fail-Closed Conditions

Authorization fails closed when:

- execution is not ready;
- approval is missing or invalid;
- approval lineage is inconsistent;
- chain continuity breaks;
- replay is corrupt;
- packet or candidate lineage is corrupt;
- execution has already started;
- the packet already claims authorization;
- authority continuity is violated;
- hash integrity fails.

## CLI Before And After

Before:

```text
Execution Status: EXECUTION_READY
Execution has not started.
```

After:

```text
Execution Status: EXECUTION_READY
Execution has not started.

Execution Authorization
Authorization Status: EXECUTION_AUTHORIZED
No Worker has been assigned, dispatched, invoked, or executed.
```

## Acceptance Results

| Scenario | Result |
| --- | --- |
| Create a filesystem Worker | `EXECUTION_READY -> EXECUTION_AUTHORIZED` |
| Improve trading strategy, then approve | `EXECUTION_READY -> EXECUTION_AUTHORIZED` |
| Corrupt execution packet | `FAILED_CLOSED` |
| Corrupt authorization replay | Reconstruction fails closed |

## Remaining Gap Before First Worker Invocation

- Worker assignment must bind an eligible registered Worker.
- Dispatch must bind the assigned Worker to the authorization.
- Worker invocation request and invocation runtime remain required.
- Worker sandbox, result validation, and post-execution replay review remain
  required before real execution.
