# Intent Classifier Blockers V1

Status: blocker review before implementation.

## Genuine Blockers

No constitutional or architectural blocker prevents a minimal classifier V1.

## Must Fix In Implementation

The first implementation must include:

- explicit artifact schema
- append-only replay persistence
- artifact hash validation
- fail-closed invalid and ambiguous classification handling
- non-authority guarantees in every artifact
- no destination invocation

## Refinements

These improve quality but do not block V1:

- conversation-only lifecycle completion
- operator-facing classification summary
- full routing runtime
- route replay summary
- pressure validation expansion

## Deferred Items

These must wait:

- correction loops
- memory-assisted classifier behavior
- provider-assisted classifier behavior
- autonomous routing
- provider selection
- worker selection

## Blocker Classification

`IMPLEMENTATION_BLOCKERS`: `NONE_FOR_MINIMAL_V1`

`DEFERRED_CAPABILITIES`: `PRESENT`

