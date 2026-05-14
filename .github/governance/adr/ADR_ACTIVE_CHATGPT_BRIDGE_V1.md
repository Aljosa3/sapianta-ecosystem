# ADR: Active ChatGPT Bridge v1

## Context

SAPIANTA / AiGOL now has ChatGPT ingress, natural-language-to-envelope conversion, active provider invocation, a result return loop, and governed execution sessions.

Manual copy/paste remains the practical gap between interaction input and governed execution output. `ACTIVE_CHATGPT_BRIDGE_V1` begins closing that gap by defining a deterministic bridge surface while preserving all bounded governance constraints.

## Decision

Introduce `ACTIVE_CHATGPT_BRIDGE_V1` as a single-session, single-provider, single-invocation bridge.

The bridge accepts ChatGPT-facing input, binds it to ingress and NL-to-envelope artifacts, invokes exactly one explicitly requested provider through existing active invocation/session layers, returns the result through the result loop, and creates a ChatGPT-facing response payload.

The bridge is not an orchestration engine.

## Consequences

Positive:

- ChatGPT-facing inputs can be connected to governed execution session outputs
- response payloads preserve lineage and evidence references
- copy/paste reduction becomes structurally possible
- one bridge request maps to one governed session
- one governed session maps to one provider invocation

Tradeoffs:

- no retries
- no fallback behavior
- no provider routing
- no autonomous interpretation
- no scheduling or follow-up task execution

## Explicit Non-Goals

- autonomous orchestration
- autonomous planning
- provider routing
- adaptive provider selection
- retries
- fallback logic
- background execution
- continuous loops
- scheduling
- hidden prompt rewriting
- memory mutation
- multimodal orchestration
- unrestricted execution

## Relationship

This bridge depends on:

- `CHATGPT_INGRESS_BRIDGE_V1`
- `NATURAL_LANGUAGE_TO_ENVELOPE_V1`
- `GOVERNED_EXECUTION_SESSION_V1`
- `ACTIVE_PROVIDER_INVOCATION_V1`
- `RESULT_RETURN_LOOP_V1`
- `TRANSPORT_BRIDGE_V1`

## Invariants

`ACTIVE_CHATGPT_BRIDGE != ORCHESTRATION`

`BRIDGE_RESPONSE != AUTONOMOUS INTERPRETATION`

`CHATGPT_INPUT != EXECUTION AUTHORITY`
