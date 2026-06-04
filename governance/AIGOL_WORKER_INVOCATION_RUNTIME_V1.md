# AIGOL_WORKER_INVOCATION_RUNTIME_V1

## Status

Certified current-chain Worker invocation runtime.

## Final Classification

```text
AIGOL_WORKER_INVOCATION_RUNTIME_STATUS = CERTIFIED
```

## Purpose

Transform a replay-valid `WORKER_DISPATCHED` artifact into `WORKER_INVOKED`.

This runtime consumes `WORKER_DISPATCH_ARTIFACT_V1` and creates
`WORKER_INVOCATION_ARTIFACT_V1`. It establishes the governed invocation boundary
for an assigned and dispatched Worker.

## Lifecycle

```text
WORKER_DISPATCHED
-> WORKER_INVOKED
```

## Input

The runtime consumes:

- `WORKER_DISPATCH_ARTIFACT_V1`;
- its replay reference.

The runtime reconstructs Worker dispatch replay before invocation.

## Output Artifacts

The runtime persists:

- `WORKER_INVOCATION_EVIDENCE_ARTIFACT_V1`;
- `WORKER_INVOCATION_CLASSIFICATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_ARTIFACT_V1`;
- `WORKER_INVOCATION_RESULT_ARTIFACT_V1`.

## Invocation Model

`WORKER_INVOCATION_ARTIFACT_V1` records:

- assigned Worker identity;
- assigned Worker family;
- Worker role;
- Worker dispatch reference and hash;
- Worker assignment reference and hash;
- Worker invocation request reference and hash;
- execution authorization reference and hash;
- execution packet reference and hash;
- allowed outputs;
- forbidden operations;
- validation requirements;
- chain id;
- replay reference.

Invocation marks the Worker as invoked. It does not validate results.

## Validation

The runtime verifies:

- dispatch lineage;
- assignment lineage;
- invocation request lineage;
- authorization lineage;
- execution packet lineage;
- Worker identity continuity;
- chain continuity;
- replay continuity;
- authority continuity;
- artifact and wrapper hash continuity;
- allowed-output and forbidden-operation propagation.

## Fail-Closed Conditions

The runtime fails closed when:

- dispatch mismatches;
- assignment lineage mismatches;
- authorization lineage mismatches;
- execution packet lineage mismatches;
- Worker identity mismatches;
- replay is corrupt;
- authority continuity is violated;
- chain continuity breaks.

## Authority Boundaries

This runtime may:

- invoke a dispatched Worker.

This runtime may not:

- validate results;
- approve results;
- create approvals;
- modify governance;
- mutate existing replay;
- perform post-execution replay review;
- terminate the governed execution lifecycle.

## Replay Model

Replay is append-only and records:

```text
invocation_evidence_recorded
-> invocation_classification_recorded
-> invocation_artifact_recorded
-> invocation_result_recorded
```

Replay reconstruction verifies:

- invocation continuity;
- dispatch continuity;
- authority continuity;
- replay continuity;
- hash continuity.

## CLI Before And After

Before:

```text
Worker Dispatch
Dispatch Status: WORKER_DISPATCHED
```

After:

```text
Worker Invocation
Invocation Status: WORKER_INVOKED

No result validation yet.
No replay review yet.
No termination yet.
```

## Acceptance Results

| Scenario | Result |
| --- | --- |
| Filesystem Worker | `WORKER_DISPATCHED -> WORKER_INVOKED` |
| Monitoring Worker | `WORKER_DISPATCHED -> WORKER_INVOKED` |
| Approved Trading Improvement | `Approve -> WORKER_DISPATCHED -> WORKER_INVOKED` |

## Remaining Blockers Before First Governed Result Capture

The next missing binding is governed Worker result capture.

Before first governed result capture, AiGOL still needs a runtime that consumes
`WORKER_INVOCATION_ARTIFACT_V1`, captures Worker output, enforces allowed-output
and forbidden-operation scope, and produces a replay-visible Worker result
artifact without approving or validating that result.
