# Canonical Lifecycle Semantics V1

Status: lifecycle vocabulary stabilization only.

## Canonical Definition

A lifecycle is an explicit replay-visible progression through named states.

Lifecycle semantics are state visibility rules. They are not runtime execution, worker dispatch, autonomous planning, or orchestration intelligence.

## Canonical Terms

### State

A state is a named lifecycle condition with a bounded meaning.

State does not imply execution authority.

### Transition

A transition is a replay-visible movement from one state to another.

Transitions must be deterministic, append-only, and fail-closed on ambiguity.

### Termination

Termination is a final lifecycle state that prevents hidden continuation.

Termination must be explicit and replay-visible.

### FAILED

`FAILED` is a terminal fail-closed state.

`FAILED` does not mean retry, repair, autonomous recovery, or continuation.

### Resurrection Prohibition

Resurrection prohibition means no terminal lifecycle state can move back to an active or pre-terminal state.

Attempted resurrection must fail closed.

## Canonical Orchestration Lifecycle Vocabulary

The canonical orchestration lifecycle states are:

- `REQUESTED`
- `GOVERNANCE_VALIDATED`
- `AUTHORIZED`
- `ACTIVE`
- `TERMINATED`
- `FAILED`

`ACTIVE` is a lifecycle-visible state only. It does not mean runtime orchestration, worker dispatch, execution coordination, adaptive planning, or autonomous coordination.

`TERMINATED` and `FAILED` are terminal.

## Canonical Rule

Lifecycle vocabulary must not create hidden runtime behavior.

If a lifecycle term can be misread as execution, dispatch, persistence, or autonomous continuation, the artifact must explicitly constrain it.

