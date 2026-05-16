# ADR_GOVERNED_EXECUTION_RELAY_V1

## Decision

Introduce a deterministic governed execution relay over the existing governed execution exchange and terminal attachment outputs.

## Rationale

The exchange layer formalizes request/result pairing. The relay layer makes bounded stdin/stdout transport continuity explicit, so terminal command input and terminal output return can be verified as one governed relay transaction.

## Boundary

The relay is not autonomous execution, orchestration, routing, retries, hidden memory, unrestricted subprocess execution, or a new shell surface. It does not modify prior contracts or fabricate missing continuity.

## Consequence

Governed command/output relay becomes replay-visible and fail-closed while preserving the existing bounded runtime architecture.
