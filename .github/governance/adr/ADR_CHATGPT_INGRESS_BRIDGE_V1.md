# ADR: ChatGPT Ingress Bridge v1

## Context

AiGOL has a semantic NL-to-envelope layer, execution envelopes, provider abstraction, adapter runtime, and bounded transport bridge. The remaining boundary is explicit ChatGPT ingress: the interaction surface must be captured and bound to semantic governance without gaining authority.

## Decision

Introduce `CHATGPT_INGRESS_BRIDGE_V1`.

The bridge creates deterministic ingress sessions and requests, binds ChatGPT-originated natural language to the NL envelope subsystem, validates ingress state fail-closed, and emits replay-safe ingress evidence.

## Core Invariants

```text
CHATGPT != GOVERNANCE
NATURAL_LANGUAGE != EXECUTION
INGRESS != EXECUTION AUTHORITY
PROPOSAL != EXECUTION
REPLAY MUST REMAIN DETERMINISTIC
```

## Why ChatGPT Is Not Governance

ChatGPT is an interaction surface. It may capture requests, preserve conversation lineage, and initiate semantic proposal generation. It cannot approve, govern, execute, route, schedule, retry, or mutate memory.

## Why Ingress Is Not Execution Authority

Ingress prepares governance-visible proposals only. It does not call providers, invoke adapters, execute transport, or run shell/network operations.

## Why Replay-Safe Conversation Capture Matters

The original request, normalized text, session identity, request identity, timestamp, replay binding, and semantic lineage are preserved so downstream governance can inspect what was proposed without treating the prompt as authority.

## Consequences

Positive:

- ChatGPT interaction becomes replay-visible.
- Natural language is bound to deterministic semantic governance.
- Envelope proposals remain non-authoritative.
- Ingress validation fails closed.

Tradeoffs:

- No autonomous execution is introduced.
- No provider calls are introduced.
- Request classification remains deterministic and conservative.

## Explicit Non-Goals

- Autonomous execution.
- Provider orchestration.
- Hidden routing.
- Retries.
- Fallback logic.
- Adaptive execution.
- Background agents.
- Continuous runtime loops.
- Self-modifying governance.
- Hidden prompt rewriting.
- Direct provider execution.
- Network execution.
- Shell execution.
- Scheduling.
- Memory mutation.
- Autonomous approval.
