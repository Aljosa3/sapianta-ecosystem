# AIGOL ERR Shared Infrastructure Scope Lock V1

Status: finalized scope lock declaration.

Purpose: lock ERR as passive shared infrastructure after provider and worker selection validation.

## Locked Scope

ERR is locked as passive resource metadata and replay-visible selection evidence infrastructure.

The validated ERR surface supports:

- `COGNITION_PROVIDER` lookup;
- `EXECUTION_WORKER` lookup;
- capability-based selection;
- `ACTIVE` status filtering;
- replay-visible selection evidence.

ERR may be consumed by governed workflows that need to resolve a bounded resource by declared capability without hardcoding the resource identity into the workflow.

## Accepted Consumers

The accepted consumers for this scope lock are:

- HIRR path:
  - Human Intent -> HIRR output -> required capability -> ERR lookup -> replay evidence.

- OCS cognition workflow:
  - OCS requests `reasoning`;
  - ERR resolves `mock_provider`;
  - OCS derives a bounded cognition-provider contract from ERR selection;
  - OCS preserves cognition governance and replay evidence.

- Worker assignment workflow:
  - Worker assignment requests `file_write`;
  - ERR resolves `mock_filesystem_worker`;
  - worker assignment compatibility checks still gate assignment;
  - worker assignment replay records ERR selection.

## Explicit Prohibitions

ERR must not:

- invoke providers;
- invoke workers;
- dispatch;
- rank resources;
- optimize resource selection;
- authorize actions;
- govern;
- mutate replay history;
- become ELL;
- introduce marketplace behavior;
- introduce lifecycle engines;
- introduce autonomous discovery;
- introduce attachment lifecycle state machines;
- silently replace OCS orchestration;
- silently replace worker assignment compatibility checks.

ERR selection evidence must remain non-authoritative. Selection does not equal approval, authorization, dispatch, invocation, or execution.

## Boundary Invariants

The following boundary model is locked:

```text
Human = authority layer
HIRR = intent resolution path
OCS = orchestration layer
ERR = passive resource lookup and selection evidence
Providers = cognition only
Workers = execution only
Replay = evidence continuity
```

Providers may not invoke workers.

Workers may not invoke providers.

ERR may not invoke either.

## Future Extension Rule

Any new ERR capability, resource type, status value, consumer workflow, selection field, or replay evidence expansion must pass through governed change with tests.

At minimum, future ERR evolution must prove:

- existing provider lookup remains replay-visible;
- existing worker lookup remains replay-visible;
- inactive resources remain excluded;
- ERR still performs no invocation, dispatch, authorization, governance, ranking, optimization, lifecycle management, or replay mutation;
- consumer workflows remain fail-closed when ERR cannot resolve a valid resource.

## ELL Recommendation

ELL should remain deferred.

The completed milestones show that ERR already covers the required shared infrastructure function: passive capability lookup for cognition providers and execution workers with replay evidence.

ELL should not be introduced unless a future governed milestone proves a distinct need for lifecycle, attachment, streaming, invocation, or cross-resource coordination semantics that cannot be safely represented as passive ERR lookup plus existing OCS and worker-governance workflows.

Until that evidence exists, introducing ELL would duplicate or blur the locked ERR boundary.

## Governance Interpretation

This scope lock does not make ERR constitutional governance, OCS orchestration, worker dispatch, or provider invocation infrastructure.

It locks ERR as shared infrastructure only in the narrow sense of:

```text
resource metadata + capability lookup + ACTIVE filtering + replay-visible selection evidence
```

All runtime authority remains outside ERR.
