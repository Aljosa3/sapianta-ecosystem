# AIGOL ELL Deferred V1

Status: finalized governance decision.

Purpose: formally evaluate whether ELL is required after ERR provider and worker selection validation.

## Evaluation Inputs

This decision evaluates ELL after the following milestones:

- `AIGOL_ERR_V0`
- `AIGOL_ERR_OCS_INTEGRATION_V1`
- `AIGOL_WORKER_RESOURCE_SELECTION_V1`
- `AIGOL_ERR_SHARED_INFRASTRUCTURE_SCOPE_LOCK_V1`

## Original ELL Responsibilities

ELL was considered as a possible future runtime layer if AiGOL needed capabilities beyond passive resource lookup.

Potential ELL responsibilities were:

- external resource lifecycle management;
- attachment lifecycle state;
- provider invocation lifecycle;
- worker invocation lifecycle;
- streaming or long-running interaction state;
- cross-resource coordination;
- retry and continuation control;
- resource availability beyond `ACTIVE` / `INACTIVE`;
- runtime execution mediation between providers and workers.

These responsibilities imply active runtime behavior.

## ERR Capability Comparison

ERR now covers the validated shared-infrastructure need:

- `COGNITION_PROVIDER` lookup;
- `EXECUTION_WORKER` lookup;
- capability-based selection;
- `ACTIVE` filtering;
- replay-visible selection evidence;
- HIRR path lookup;
- OCS cognition workflow lookup;
- worker assignment workflow lookup.

ERR does not invoke, dispatch, authorize, govern, rank, optimize, manage lifecycle, or mutate replay history.

This is sufficient for the architectural problem that triggered ERR:

```text
How can AiGOL locate a provider or worker by capability without hardcoded resource identity inside OCS or worker assignment?
```

## Remaining Unmet Requirements

The following remain unmet by design:

- external lifecycle management;
- attachment lifecycle state machines;
- streaming runtime state;
- multi-resource coordination;
- retry orchestration;
- dynamic routing;
- provider or worker invocation mediation;
- marketplace or ranking behavior;
- cost or latency optimization.

No current replay evidence proves these are required for Product 1 or for the validated AiGOL flow.

## Runtime Evidence Assessment

Runtime evidence supports deferral rather than activation:

- OCS can request `reasoning` and receive `mock_provider` through ERR.
- Worker assignment can request `file_write` and receive `mock_filesystem_worker` through ERR.
- Replay records both selections.
- Fail-closed behavior is preserved when no active matching resource exists.
- Existing OCS and worker-governance workflows continue to own orchestration and compatibility checks.

The evidence shows that passive ERR lookup solves the immediate architectural problem without ELL.

## Decision

ELL is not justified at this time.

ELL is deferred.

No ELL runtime, lifecycle engine, attachment manager, invocation mediator, streaming controller, routing optimizer, or cross-resource coordinator should be implemented under the current evidence baseline.

## Reactivation Criteria

ELL may be reconsidered only through governed change if future evidence proves at least one of the following requirements cannot be safely handled by ERR plus existing OCS and worker-governance workflows:

- a replay-visible external resource lifecycle must be managed independently of OCS and worker assignment;
- attachment state must persist across governed turns with explicit lifecycle transitions;
- streaming or long-running provider or worker interactions require deterministic replay semantics;
- cross-resource coordination is required and cannot remain inside OCS;
- retry or continuation semantics require a separate bounded runtime layer;
- provider or worker invocation mediation is needed without violating provider/worker separation;
- `ACTIVE` / `INACTIVE` is insufficient and additional status semantics are governance-approved with tests.

Any reactivation must include:

- a governance proposal;
- explicit non-goals;
- replay evidence requirements;
- fail-closed tests;
- authority-boundary tests;
- proof that ERR remains passive;
- proof that ELL does not become OCS, worker dispatch, governance, marketplace, or autonomous discovery.

## Final Recommendation

Keep ELL deferred.

Preserve ERR as the shared passive infrastructure boundary:

```text
resource metadata + capability lookup + ACTIVE filtering + replay-visible selection evidence
```

Continue using OCS for orchestration, worker assignment for worker compatibility and assignment, governance for authorization, and replay for evidence continuity.

Do not introduce ELL until runtime evidence proves a distinct governed need that cannot be met by the current ERR-centered architecture.
