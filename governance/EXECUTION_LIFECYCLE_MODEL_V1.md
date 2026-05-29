# Execution Lifecycle Model V1

Status: execution lifecycle semantics only.

## Lifecycle States

### REQUESTED

An execution participation request has been explicitly proposed.

Properties:

- replay-visible
- bounded
- non-authoritative
- not yet validated

### VALIDATED

The execution request has been checked for constitutional admissibility, lineage continuity, replay visibility, and bounded scope.

Properties:

- governance-constrained
- replay-visible
- authority-separated
- not execution completion

### AUTHORIZED

The request has explicit permission to proceed within the bounded execution model.

Properties:

- explicit
- scoped
- replay-visible
- non-transferable

Authorization does not imply orchestration, worker dispatch, filesystem access, network access, hidden continuation, or future execution authority.

### EXECUTED

The bounded execution participation completed within the authorized scope.

Properties:

- replay-visible
- lineage-bound
- bounded
- non-persistent

`EXECUTED` does not imply autonomous continuation or authority expansion.

### FAILED

The execution lifecycle failed closed because request, validation, authorization, lineage, replay, or transition semantics became invalid or ambiguous.

Properties:

- terminal
- replay-visible
- deterministic
- non-recovering

### TERMINATED

The execution lifecycle closed explicitly after completion or bounded lifecycle conclusion.

Properties:

- terminal
- deterministic
- replay-visible
- non-persistent

## Transition Rules

Canonical success path:

```text
REQUESTED -> VALIDATED -> AUTHORIZED -> EXECUTED -> TERMINATED
```

Fail-closed transitions may occur from any non-terminal state:

```text
REQUESTED -> FAILED
VALIDATED -> FAILED
AUTHORIZED -> FAILED
EXECUTED -> FAILED
```

`FAILED` and `TERMINATED` are terminal.

## Prohibited Transitions

The lifecycle prohibits:

- hidden transitions
- implicit continuation
- resurrection after `FAILED`
- resurrection after `TERMINATED`
- transition from `EXECUTED` to new execution request
- authority inheritance drift
- orchestration dispatch transition
- worker dispatch transition

## Invalid Transition Handling

Invalid transitions must fail closed, preserve replay evidence, and terminate the execution lifecycle.

