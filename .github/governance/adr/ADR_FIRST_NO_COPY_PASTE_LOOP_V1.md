# ADR: First No-Copy/Paste Loop v1

## Context

SAPIANTA / AiGOL now has a bounded active ChatGPT bridge, governed execution sessions, active provider invocation, and a result return loop.

The remaining operational gap is manual transfer between interaction-facing input and governed execution output. `FIRST_NO_COPY_PASTE_LOOP_V1` establishes a deterministic continuity layer for a single governed execution pass.

## Decision

Introduce `FIRST_NO_COPY_PASTE_LOOP_V1` as a replay-safe no-copy/paste loop that accepts one ChatGPT-facing request, executes through the existing bounded bridge/session/invocation/result-return substrate, and returns one ChatGPT-facing response payload.

The loop is not orchestration. It does not retry, route, fallback, schedule, recursively execute, or continue autonomously.

## Consequences

Positive:

- governed request propagation becomes explicit
- governed result propagation becomes explicit
- manual copy/paste can be reduced for one bounded pass
- lineage continuity is visible across the whole interaction loop
- response delivery remains deterministic and replay-safe

Tradeoffs:

- no autonomous continuation
- no dynamic provider selection
- no retries or fallback behavior
- no multi-step planning

## Boundary Invariants

- `CHATGPT != GOVERNANCE`
- `NATURAL_LANGUAGE != EXECUTION_AUTHORITY`
- `PROPOSAL != EXECUTION`
- `PROVIDER != GOVERNANCE`
- `LOOP != ORCHESTRATION`

## Explicit Non-Goals

- autonomous orchestration
- recursive self-improvement
- multi-agent planning
- adaptive routing
- retries
- fallback execution
- hidden execution
- unrestricted provider authority
- autonomous workflow continuation
- background execution
- speculative execution
- memory mutation
- execution scheduling
