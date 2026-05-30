# Intent Routing Authority Guarantees V1

Status: authority preservation rules for intent routing.

## Authority Preservation Classification

`INTENT_ROUTING_AUTHORITY_PRESERVATION`: `PRESERVABLE`

## Core Guarantee

Routing selects a destination.

Routing does not:

- govern
- authorize
- execute
- propose
- retrieve memory
- command a provider
- command a worker

## Invariant Preservation

Routing preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

by ensuring:

- provider routes end at provider proposal boundary
- memory routes end at reference-only retrieval boundary
- execution routes end before authorization
- conversation routes do not imply execution or provider invocation
- all route outcomes are replay-visible

## Never Delegated Authority

Routing must never receive:

- constitutional authority
- governance authority
- authorization authority
- execution authority
- worker authority
- replay mutation authority
- provider authority

## Boundary Consequence

If a routing step attempts to authorize, execute, command a provider, command a worker, or mutate replay, it must fail closed.

