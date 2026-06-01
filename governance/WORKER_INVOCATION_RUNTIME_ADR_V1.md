# WORKER_INVOCATION_RUNTIME_ADR_V1

## Status

Accepted as foundation review.

## Context

AiGOL has:

- Worker Runtime;
- Dispatch Runtime Foundation.

Workers can be assigned. Dispatch governance is defined as the boundary after assignment and before invocation. The next missing boundary is the governed transition from dispatched worker eligibility to worker invocation.

## Decision

AiGOL will treat worker invocation as an explicit governance boundary between `DISPATCHED` and future worker execution.

Only AiGOL governance may record invocation.

Invocation requires replay-valid evidence that:

- dispatch exists;
- dispatch status is `DISPATCHED`;
- worker assignment exists;
- worker identity matches assignment and dispatch evidence;
- readiness evidence exists;
- execution request lineage exists;
- invocation parameters are bounded and hashable;
- invocation parameters do not expand scope;
- no cancellation, expiry, execution, or completion has occurred;
- invocation validation is recorded in replay.

## Non-Goals

This ADR does not implement:

- invocation runtime code;
- worker execution;
- execution completion;
- worker result persistence;
- worker termination evidence;
- provider authority;
- automatic invocation;
- worker self-invocation.

## Consequences

Dispatch evidence remains non-executing until a future invocation runtime records replay-valid `WORKER_INVOCATION_ARTIFACT_V1` evidence.

Future execution runtime must reject any worker activity that lacks replay-valid invocation evidence.

Provider and worker authority remain isolated from invocation validation.

Replay reconstructs invocation history, but replay does not authorize invocation.

## Known Gaps

- No invocation runtime implementation exists in this foundation.
- No invocation runtime tests exist in this foundation.
- Dispatch runtime itself remains foundation-only.
- No worker execution runtime exists.
- No completion or result persistence runtime exists.
- No worker termination evidence runtime exists.

## Constitutional Alignment

The decision preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

AiGOL governs invocation. Future workers execute only after a separate execution boundary. Replay records the invocation decision and bounded parameter envelope.
