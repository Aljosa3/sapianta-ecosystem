# ADR_GOVERNED_LOCAL_RUNTIME_BRIDGE_V1

## Decision

Introduce a deterministic governed local runtime bridge over the existing governed execution relay.

## Rationale

The relay layer proves bounded command/output continuity. The bridge layer adds explicit bounded runtime transport attachment identity so local runtime transport can be certified without hidden state or manual continuity reconstruction.

## Boundary

The bridge is not autonomous execution, orchestration, retries, routing, unrestricted subprocess execution, hidden memory, or a network transport surface. It does not alter prior contracts or fabricate missing lineage.

## Consequence

Local runtime transport continuity becomes replay-visible, bounded, and fail-closed while preserving the existing governed runtime stack.
