# ADR: REAL_INTERACTION_INGRESS_EGRESS_ADAPTER_V1

## Status

Accepted.

## Decision

Add a deterministic local file ingress/egress adapter around the interaction transport bridge.

## Boundaries

The adapter reads one bounded JSON ingress artifact and writes one bounded JSON egress artifact. It does not monitor directories, run daemons, expose APIs, orchestrate, retry, route, persist memory, or run asynchronously.

## Consequence

Local artifact continuity becomes replay-visible without creating a broader transport or service layer.
