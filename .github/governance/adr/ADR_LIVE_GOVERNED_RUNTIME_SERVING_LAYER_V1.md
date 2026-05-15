# ADR: LIVE_GOVERNED_RUNTIME_SERVING_LAYER_V1

## Status

Accepted.

## Decision

Add a reusable governed runtime serving identity so multiple interaction turns attach directly to the same active serving layer. This removes manual runtime reattachment while remaining deterministic lineage, not a daemon or autonomous service.
