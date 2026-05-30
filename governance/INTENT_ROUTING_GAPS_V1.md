# Intent Routing Gaps V1

Status: gap analysis for canonical intent routing.

## Critical Gaps

Before runtime routing can be implemented, AiGOL still needs:

- explicit `INTENT_ROUTING_ARTIFACT` schema
- deterministic destination vocabulary
- replay persistence rules for route artifacts
- fail-closed ambiguity rules in runtime form
- proof that routing output cannot authorize or execute

## Important Gaps

Useful but not strictly blocking for the routing model:

- conversation-only destination lifecycle
- operator-facing route explanation format
- route replay summary view
- route pressure validation plan

## Optional Gaps

Future conveniences that should not drive architecture early:

- confidence scoring
- route suggestions
- route correction loop
- provider selection
- worker selection
- intent examples catalog

## Current Readiness

The model is ready for future implementation review, not runtime implementation.

`INTENT_ROUTING_MODEL_STATUS`: `READY_WITH_GAPS`

