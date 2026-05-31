# FIRST_USEFUL_AIGOL_ADR_V1

## Decision

Select configuration/repository marker creation as `FIRST_USEFUL_AIGOL_V1`.

## Context

`FIRST_END_TO_END_GOVERNED_OPERATION_V1` proved the constitutional path:

```text
Human
↓
Provider
↓
Proposal
↓
Governed Authorization
↓
Authorized Worker Request
↓
Worker
↓
Replay
```

The next milestone requires practical value rather than additional architecture.

## Rationale

Configuration and repository operations are valuable because small file mutations can matter in real systems. A direct provider call can propose such a mutation, but cannot make it auditable, bounded, authorized, and replay-reconstructable.

The existing minimal filesystem worker is sufficient for the smallest useful operation. It creates one file only after governed authorization and rejects unresolved or out-of-scope states.

## Alternatives Considered

Filesystem-only demo: rejected as too generic unless tied to a real governance use case.

Code generation: deferred because it requires review semantics beyond the current minimal proof.

API invocation: deferred because it would introduce network/API execution scope.

Document processing: deferred because useful execution would require a document worker or parser boundary.

Repository operations via git: deferred because git mutation would add command/execution semantics beyond one bounded file creation.

## Consequences

AiGOL can now claim practical usefulness in a narrow but real sense:

- untrusted proposal converted to governed operation;
- authorization evidence exists before worker execution;
- worker execution is bounded;
- replay reconstructs the entire event;
- audit evidence is deterministic.

## Non-Goals

This ADR does not authorize broader filesystem mutation, shell execution, API execution, provider execution, autonomous planning, orchestration, or multi-worker operation.

