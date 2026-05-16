# ADR_GOVERNED_RUNTIME_EXECUTION_COMMIT_V1

## Decision

Introduce a deterministic governed runtime execution commit layer above the runtime activation gate.

## Rationale

An approved activation proves permission, not execution. The commit layer records the separate transition from approved activation into a bounded execution lifecycle and preserves the later result-capture and response-return identities.

## Boundary

The commit layer is not autonomous execution, orchestration, routing, retries, hidden memory, unrestricted subprocess execution, or provider switching. It adds only replay-visible lifecycle evidence over existing governed artifacts.

## Consequence

Activation approval, execution commitment, result capture, and governed response return become distinct deterministic states with explicit lineage continuity.
