# ADR: Governed Execution Session v1

## Context

SAPIANTA / AiGOL now has bounded ChatGPT ingress, natural-language-to-envelope transformation, execution envelopes, active provider invocation, and a result return loop.

Those components need a deterministic session layer that links their evidence into one replay-safe lifecycle without becoming an orchestration system.

## Decision

Introduce `GOVERNED_EXECUTION_SESSION_V1` as the first canonical governed execution session layer.

The session binds:

- `CHATGPT_INGRESS_BRIDGE_V1`
- `NATURAL_LANGUAGE_TO_ENVELOPE_V1`
- `EXECUTION_ENVELOPE_MODEL_V1`
- `ACTIVE_PROVIDER_INVOCATION_V1`
- `RESULT_RETURN_LOOP_V1`

The session lifecycle is explicit, ordered, and fail-closed. One session binds one envelope, one provider identity, one invocation, and one result return payload.

## Consequences

Positive:

- full governed execution lineage becomes session-visible
- replay-safe evidence can be validated at session level
- provider, envelope, invocation, and result identities remain consistent
- future user-facing execution flows gain a stable session boundary

Tradeoffs:

- the session does not plan follow-up work
- the session does not retry or recover automatically
- the session does not select or route providers
- session completion requires complete upstream artifacts

## Explicit Non-Goals

- autonomous orchestration
- autonomous planning
- provider routing
- adaptive optimization
- retries
- fallback logic
- background execution
- continuous loops
- scheduling
- autonomous next-step execution
- hidden memory mutation
- multimodal orchestration
- real provider API expansion

## Invariants

`SESSION != ORCHESTRATION`

`SESSION != AUTONOMOUS EXECUTION`
