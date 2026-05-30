# Intent Routing Model V1

Status: canonical model-only intent routing definition.

This milestone defines how a Human Prompt may be routed to constitutionally valid destinations.

It does not implement an intent classifier, routing engine, routing runtime, autonomous prompt handling, automatic provider invocation, automatic execution, worker invocation, provider selection, worker selection, or correction loop.

## Core Routing Principle

Intent routing is destination selection evidence.

It is not:

- governance authority
- execution authority
- provider authority
- worker authority
- authorization
- execution
- proposal generation
- memory retrieval

Routing must preserve:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Canonical Question

When AiGOL receives a Human Prompt, the routing model asks:

```text
Which governed destination may receive this prompt?
```

It does not answer:

```text
Should execution be authorized?
Should a worker execute?
Should a provider be trusted?
Should governance mutate?
```

## Valid Destinations

The current destination set is:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

Destination maturity differs. Memory consultation, provider proposal, and execution request have defined downstream boundaries. Conversation remains partial.

## Routing Outcome

A future routing boundary should emit an `INTENT_ROUTING_ARTIFACT` containing:

- prompt reference
- candidate destination
- route classification
- route status
- ambiguity status
- replay lineage
- non-authority guarantees
- failure reason when failed closed

The artifact must not contain:

- authorization decision
- execution request
- provider command
- worker command
- governance decision

## Final Classification

`INTENT_ROUTING_MODEL_STATUS`: `READY_WITH_GAPS`

`INTENT_ROUTING_AUTHORITY_PRESERVATION`: `PRESERVABLE`

`INTENT_ROUTING_REPLAY_VISIBILITY`: `MANDATORY`

## Direct Answer

AiGOL can define intent routing now as a replay-visible, fail-closed, non-authoritative destination selection model.

Implementation should wait until the routing artifact and classifier contract are explicitly introduced.

