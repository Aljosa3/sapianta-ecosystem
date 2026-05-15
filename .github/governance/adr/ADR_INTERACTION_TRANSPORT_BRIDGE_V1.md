# ADR: INTERACTION_TRANSPORT_BRIDGE_V1

## Status

Accepted.

## Context

Human interaction continuity exists, but replay-safe transport continuity still needs explicit lineage binding between the human-facing view and governed execution references.

## Decision

Add a deterministic interaction transport bridge with explicit lineage references and mechanical response normalization.

## Boundaries

The bridge does not orchestrate, retry, fallback, route, switch providers, continue autonomously, persist memory, run asynchronously, expose unrestricted APIs, or broaden shell authority.

## Consequences

Transport continuity is replay-visible and fails closed whenever execution lineage or normalization proof is incomplete.
