# ADR: ChatGPT Ingress Finalization v1

## Context

`CHATGPT_INGRESS_BRIDGE_V1` introduced the first bounded ChatGPT ingress bridge for SAPIANTA / AiGOL.

The bridge connects ChatGPT interaction capture to the natural-language-to-envelope subsystem and produces bounded `ExecutionEnvelope` proposals without introducing runtime execution, provider invocation, routing, retries, fallback logic, or orchestration.

Finalization is needed before `ACTIVE_PROVIDER_INVOCATION_V1` so future provider invocation work inherits a frozen semantic boundary rather than treating conversational input as authority.

## Decision

Finalize `CHATGPT_INGRESS_BRIDGE_V1` as `FINALIZE_CHATGPT_INGRESS_BRIDGE_V1`.

The finalized boundary is:

- `CHATGPT != GOVERNANCE`
- `NATURAL_LANGUAGE != EXECUTION`
- `INGRESS != RUNTIME`
- `INGRESS != EXECUTION_AUTHORITY`
- `PROPOSAL != EXECUTION`

ChatGPT remains an interaction layer only. Natural language remains governance input only. Ingress remains proposal-only. Runtime execution and provider invocation remain excluded until a later milestone explicitly introduces them under governed constraints.

## Consequences

Positive:

- ingress semantics are replay-safe and explicit
- natural language cannot become execution authority
- bounded proposal generation is separated from runtime execution
- future active provider invocation has a stable semantic baseline
- governance-visible ingress evidence is preserved

Tradeoffs:

- provider invocation remains unavailable
- runtime execution remains unavailable
- additional governance evidence is required before active execution milestones

## Explicit Non-Goals

- provider invocation
- runtime execution
- orchestration
- routing
- retries
- fallback logic
- autonomous execution
- hidden prompt rewriting
- memory mutation

## Future Dependency

`ACTIVE_PROVIDER_INVOCATION_V1` must build on this finalization boundary and must not reinterpret ChatGPT, natural language, ingress, or envelope proposals as execution authority.
