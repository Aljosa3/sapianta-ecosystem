# AIGOL_WORKER_DISPATCH_RUNTIME_V1

## Status

Certified bounded Worker dispatch runtime.

## Final Classification

```text
AIGOL_WORKER_DISPATCH_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Transform a replay-valid `WORKER_ASSIGNED` artifact into
`WORKER_DISPATCHED` without invoking, executing, generating results, generating
code, or creating planned output files.

## Lifecycle

```text
WORKER_ASSIGNED
-> WORKER_DISPATCHED
```

## Input

The runtime consumes:

- `WORKER_ASSIGNMENT_ARTIFACT_V1`;
- its replay reference.

The runtime reconstructs Worker assignment replay and the referenced Worker
invocation request replay before dispatch.

## Output Artifacts

The runtime persists:

- `WORKER_DISPATCH_EVIDENCE_ARTIFACT_V1`;
- `WORKER_DISPATCH_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_DISPATCH_ARTIFACT_V1`;
- `WORKER_DISPATCH_RESULT_ARTIFACT_V1`.

## Dispatch Model

`WORKER_DISPATCH_ARTIFACT_V1` records:

- assigned Worker identity;
- dispatch eligibility;
- execution packet compatibility;
- role compatibility;
- authority continuity;
- replay continuity;
- assignment reference and hash;
- invocation request reference and hash;
- authorization reference and hash;
- chain id.

Dispatch is a delivery boundary only. It does not invoke the Worker.

## Validation

The runtime verifies:

- assignment lineage;
- invocation request lineage;
- authorization lineage;
- execution packet lineage;
- chain continuity;
- replay continuity;
- authority continuity;
- Worker identity continuity;
- dispatch eligibility;
- artifact and wrapper hash continuity.

## Fail-Closed Conditions

The runtime fails closed when:

- Worker identity mismatches;
- assignment reference or hash mismatches;
- execution packet mismatches;
- authority continuity is violated;
- replay is corrupt;
- chain continuity breaks.

## Authority Boundaries

This runtime may:

- dispatch an assigned Worker.

This runtime may not:

- invoke the Worker;
- execute the Worker;
- generate results;
- generate code;
- create planned output files;
- create approvals;
- modify governance;
- mutate existing replay.

## Replay Model

Replay is append-only and records:

```text
dispatch_evidence_recorded
-> dispatch_classification_recorded
-> dispatch_artifact_recorded
-> dispatch_result_recorded
```

Replay reconstruction verifies:

- dispatch continuity;
- authority continuity;
- replay continuity;
- hash continuity.

## CLI Before And After

Before:

```text
Worker Assignment
Assignment Status: WORKER_ASSIGNED
No Worker has been dispatched, invoked, or executed.
```

After:

```text
Worker Dispatch
Dispatch Status: WORKER_DISPATCHED
No Worker has been invoked, executed, or produced results.
```

## Acceptance Results

| Scenario | Result |
| --- | --- |
| Filesystem Worker | `WORKER_ASSIGNED -> WORKER_DISPATCHED` |
| Monitoring Worker | `WORKER_ASSIGNED -> WORKER_DISPATCHED` |
| Trading Improvement | `Approve -> WORKER_ASSIGNED -> WORKER_DISPATCHED` |

## Remaining Gap Before First Worker Invocation

The next missing binding is Worker invocation consumption of
`WORKER_DISPATCH_ARTIFACT_V1`.

Before first Worker invocation, AiGOL still needs a governed invocation runtime
that validates:

- dispatch lineage;
- assignment lineage;
- invocation request lineage;
- authorization lineage;
- Worker identity continuity;
- execution packet continuity;
- allowed-output scope;
- forbidden-operation scope;
- replay continuity;
- authority continuity.
