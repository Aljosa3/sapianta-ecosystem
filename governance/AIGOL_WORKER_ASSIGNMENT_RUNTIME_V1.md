# AIGOL_WORKER_ASSIGNMENT_RUNTIME_V1

## Status

Certified bounded Worker assignment runtime.

## Final Classification

```text
AIGOL_WORKER_ASSIGNMENT_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Transform a replay-valid `WORKER_INVOCATION_REQUEST_CREATED` artifact into
`WORKER_ASSIGNED` without dispatching, invoking, executing, generating code, or
creating planned output files.

## Lifecycle

```text
EXECUTION_AUTHORIZED
-> WORKER_INVOCATION_REQUEST_CREATED
-> WORKER_ASSIGNED
```

## Input

The runtime consumes:

- `WORKER_INVOCATION_REQUEST_ARTIFACT_V1`;
- its replay reference;
- a bounded registry of candidate `WORKER_ARTIFACT_V1` Worker identities.

The runtime reconstructs invocation request replay before assignment.

## Output Artifacts

The runtime persists:

- `WORKER_ASSIGNMENT_EVIDENCE_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- `WORKER_ASSIGNMENT_RESULT_ARTIFACT_V1`.

## Assignment Model

`WORKER_ASSIGNMENT_ARTIFACT_V1` determines and records:

- assigned Worker identity;
- Worker family compatibility;
- Worker role compatibility;
- execution packet compatibility;
- allowed outputs compatibility;
- forbidden operations compatibility;
- authorization reference and hash;
- invocation request reference and hash;
- chain id;
- assignment status.

Assignment is a selection boundary only. It does not dispatch or invoke the
assigned Worker.

## Validation

The runtime verifies:

- invocation request lineage;
- authorization lineage;
- packet lineage;
- candidate lineage;
- handoff lineage;
- chain continuity;
- replay continuity;
- authority continuity;
- Worker family compatibility;
- Worker role compatibility;
- execution packet compatibility;
- allowed output compatibility;
- forbidden operation compatibility;
- artifact and wrapper hash continuity.

## Fail-Closed Conditions

The runtime fails closed when:

- no compatible Worker exists;
- Worker family mismatches;
- Worker role mismatches;
- execution packet mismatches;
- allowed output scope is incompatible;
- forbidden operation scope is incompatible;
- authority continuity is violated;
- replay is corrupt;
- chain continuity breaks.

## Authority Boundaries

This runtime may:

- assign one compatible Worker.

This runtime may not:

- dispatch a Worker;
- invoke a Worker;
- execute a Worker;
- generate code;
- create planned output files;
- create results;
- create approvals;
- modify governance;
- mutate existing replay.

## Replay Model

Replay is append-only and records:

```text
assignment_evidence_recorded
-> assignment_classification_recorded
-> assignment_artifact_recorded
-> assignment_result_recorded
```

Replay reconstruction verifies:

- assignment continuity;
- authority continuity;
- replay continuity;
- hash continuity.

## CLI Before And After

Before:

```text
Worker Invocation Request
Request Status: WORKER_INVOCATION_REQUEST_CREATED
No Worker has been assigned, dispatched, invoked, or executed.
```

After:

```text
Worker Assignment
Assignment Status: WORKER_ASSIGNED
No Worker has been dispatched, invoked, or executed.
```

## Acceptance Results

| Scenario | Result |
| --- | --- |
| Filesystem Worker | `EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED -> WORKER_ASSIGNED` |
| Monitoring Worker | `EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED -> WORKER_ASSIGNED` |
| Trading Improvement | `Approve -> EXECUTION_AUTHORIZED -> WORKER_INVOCATION_REQUEST_CREATED -> WORKER_ASSIGNED` |

## Remaining Gap Before First Dispatch

The next missing binding is dispatch consumption of
`WORKER_ASSIGNMENT_ARTIFACT_V1`.

Before first dispatch, AiGOL still needs a governed dispatch runtime that
validates:

- assignment lineage;
- invocation request lineage;
- authorization lineage;
- Worker identity continuity;
- execution packet continuity;
- allowed-output scope;
- forbidden-operation scope;
- replay continuity;
- authority continuity.
