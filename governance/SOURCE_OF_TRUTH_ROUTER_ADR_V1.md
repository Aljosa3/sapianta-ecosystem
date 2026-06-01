# Source Of Truth Router ADR V1

Status: accepted foundation decision.

## Decision

AiGOL will define `SOURCE_OF_TRUTH_ROUTER_V1` as the global source-selection boundary for conversational responses.

The router will choose exactly one source strategy from:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

using canonical priority:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
```

## Context

AiGOL has certified source-specific strategies, but end-to-end validation found a missing unified router.

Without a router, source-specific runtime components can be correct individually while the conversational entry path remains unable to prove:

```text
Human Prompt
-> Resolution Strategy
-> Source of Truth
-> Response
```

for all supported sources.

## Rationale

Provider assistance must remain fallback.

Replay, governance, and constitutional memory are stronger sources for their respective truth domains.

The router prevents provider inference from replacing local evidence and makes source selection replay-visible.

## Decision Rules

1. `REPLAY` outranks all other sources for recorded operational truth.
2. `GOVERNANCE` outranks constitutional memory, self-resolution, and provider for governance artifact truth.
3. `CONSTITUTIONAL_MEMORY` outranks self-resolution and provider for constitutional and architectural truth.
4. `SELF_RESOLUTION` outranks provider when deterministic answer coverage is sufficient.
5. `PROVIDER` is selected only after higher-priority sources are not applicable or insufficient.
6. Provider output may not select source of truth.
7. Router selection must be replay-visible and reconstructable.
8. Ambiguity fails closed when priority or evidence cannot resolve it.

## Consequences

Future runtime implementation should create:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTION_ARTIFACT_V1
```

and replay events:

```text
SOURCE_OF_TRUTH_ROUTER_SELECTED
SOURCE_OF_TRUTH_ROUTER_RETURNED
```

The router should later invoke selected source resolvers only after this foundation is implemented.

## Non-Goals

This ADR does not implement:

- routing runtime;
- response generation;
- provider invocation;
- worker execution;
- proposal creation;
- approval changes;
- execution request creation;
- CLI epoch validation.

## Known Gaps

- Router runtime is not implemented.
- Router tests are not implemented.
- Source response envelope normalization is not implemented.
- Conversational runtime is not connected to a global source router.
- CLI validation through `aigol prompt submit` has not been rerun for all sources.

## Final Decision

The source-of-truth router foundation is accepted as a design artifact and remains ready with gaps until runtime implementation and CLI validation are completed.

```text
SOURCE_OF_TRUTH_ROUTER_FOUNDATION_STATUS = READY_WITH_GAPS
```
