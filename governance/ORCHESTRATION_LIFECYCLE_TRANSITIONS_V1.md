# Orchestration Lifecycle Transitions V1

Status: transition semantics only.

## Allowed Transition Path

The canonical orchestration lifecycle path is:

```text
REQUESTED
-> GOVERNANCE_VALIDATED
-> AUTHORIZED
-> ACTIVE
-> TERMINATED
```

Failure may occur from any non-terminal state:

```text
REQUESTED -> FAILED
GOVERNANCE_VALIDATED -> FAILED
AUTHORIZED -> FAILED
ACTIVE -> FAILED
```

`TERMINATED` and `FAILED` are terminal states.

## Transition Rules

### REQUESTED to GOVERNANCE_VALIDATED

Allowed only when the request is explicit, bounded, replay-visible, and non-authoritative.

Invalid if the request implies execution authority, hidden continuation, worker activation, recursive coordination, or governance mutation.

### GOVERNANCE_VALIDATED to AUTHORIZED

Allowed only when constitutional admissibility is explicit and authority separation is preserved.

Invalid if authorization is ambiguous, inherited implicitly, or conflated with execution permission.

### AUTHORIZED to ACTIVE

Allowed only as a modeled lifecycle transition.

Invalid if activation implies runtime orchestration, worker dispatch, autonomous planning, adaptive coordination, hidden retry behavior, or execution coordination.

### ACTIVE to TERMINATED

Allowed when lifecycle closure is explicit, bounded, deterministic, replay-visible, and non-persistent.

Invalid if termination is missing, implicit, deferred into hidden state, or replaced by continuation.

### Any Non-Terminal State to FAILED

Required when lifecycle semantics become ambiguous or invalid.

Failure must be replay-visible, terminal, and non-recovering.

## Prohibited Transitions

The following transitions are prohibited:

- `TERMINATED -> REQUESTED`
- `TERMINATED -> GOVERNANCE_VALIDATED`
- `TERMINATED -> AUTHORIZED`
- `TERMINATED -> ACTIVE`
- `TERMINATED -> FAILED`
- `FAILED -> REQUESTED`
- `FAILED -> GOVERNANCE_VALIDATED`
- `FAILED -> AUTHORIZED`
- `FAILED -> ACTIVE`
- `FAILED -> TERMINATED`
- any state to itself as hidden continuation
- any state to a recursive child orchestration chain
- any state to worker dispatch
- any state to execution coordination

## Invalid Transition Handling

All invalid transitions must:

- fail closed
- generate replay-visible violation artifacts
- terminate orchestration lifecycle
- preserve append-only lineage
- preserve authority separation

No automatic retry, hidden recovery, implicit continuation, or resurrection is permitted.

