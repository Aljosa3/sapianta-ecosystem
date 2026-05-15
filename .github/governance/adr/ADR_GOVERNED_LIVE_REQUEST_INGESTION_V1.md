# ADR_GOVERNED_LIVE_REQUEST_INGESTION_V1

## Decision

Introduce deterministic governed live request ingestion above the live governed interaction serving gateway.

## Rationale

The serving gateway already exposes bounded ingress-to-egress continuity. A governed ingestion layer adds explicit request activation identity so a live request can be admitted only when the serving continuity below it is replay-visible and valid.

## Boundary

The layer is not orchestration, not routing, not an API surface, not autonomous continuation, and not hidden memory. It does not refactor prior governance contracts or fabricate missing lineage.

## Consequence

Live request activation becomes explicit, replay-visible, bounded, and fail-closed while the existing governed runtime architecture remains unchanged beneath it.
