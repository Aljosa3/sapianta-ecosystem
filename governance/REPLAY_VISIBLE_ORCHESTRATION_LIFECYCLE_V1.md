# Replay-Visible Orchestration Lifecycle V1

Status: replay visibility model only.

## Purpose

This artifact defines how orchestration lifecycle progression remains replay-visible without becoming orchestration runtime.

Replay-visible lifecycle evidence is constitutional evidence. It is not a queue, dispatcher, worker instruction, planning runtime, or execution coordinator.

## Lifecycle Record Requirements

Each lifecycle transition should preserve:

- lifecycle identity
- previous state
- next state
- transition reason
- governance disposition
- lineage parent
- replay order
- terminal status when applicable

The record must be append-only and deterministic.

## Replay Ordering

Replay ordering must follow deterministic lifecycle progression:

```text
REQUESTED
GOVERNANCE_VALIDATED
AUTHORIZED
ACTIVE
TERMINATED
```

or a terminal failure path:

```text
REQUESTED
FAILED
```

or:

```text
REQUESTED
GOVERNANCE_VALIDATED
FAILED
```

or:

```text
REQUESTED
GOVERNANCE_VALIDATED
AUTHORIZED
FAILED
```

or:

```text
REQUESTED
GOVERNANCE_VALIDATED
AUTHORIZED
ACTIVE
FAILED
```

## Replay Invariants

Replay-visible orchestration lifecycle must preserve:

- deterministic transition order
- append-only lineage
- explicit terminal states
- no missing transitions
- no duplicate terminal states
- no hidden continuation records
- no resurrection after terminal state

## Ambiguity Handling

If replay evidence cannot prove deterministic lifecycle progression, the lifecycle must fail closed.

Ambiguity includes:

- missing transition
- duplicate transition
- non-monotonic lifecycle order
- hidden continuation signal
- authority inheritance drift
- terminal state resurrection
- recursive orchestration signal

