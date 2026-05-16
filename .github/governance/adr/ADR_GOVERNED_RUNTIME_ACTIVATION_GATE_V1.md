# ADR_GOVERNED_RUNTIME_ACTIVATION_GATE_V1

## Decision

Introduce a deterministic governed runtime activation gate above the existing governed local runtime bridge.

## Rationale

The bridge layer proves local runtime transport continuity. The activation gate adds the separate governance decision that a valid bridge is not by itself permission to enter an active runtime state. Activation must be explicit, human-approved, and replay-visible.

## Boundary

The gate is not orchestration, autonomous execution, routing, retries, hidden memory, unrestricted subprocess execution, or a new runtime service. It preserves prior contracts and adds only bounded authorization evidence.

## Consequence

Runtime activation becomes explicit, deterministic, fail-closed, and governance-verifiable while remaining distinct from runtime transport continuity.
