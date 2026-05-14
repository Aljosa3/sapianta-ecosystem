# ADR: Natural Language To Envelope v1

## Context

AiGOL has execution envelopes, provider abstraction, bounded runtime adapters, and a transport bridge. The missing boundary is semantic governance ingress: natural language must be transformed into bounded envelope proposals before execution can ever be considered.

## Decision

Introduce `NATURAL_LANGUAGE_TO_ENVELOPE_V1`.

The layer preserves raw natural language, classifies deterministic intent, evaluates admissibility, maps least-privilege authority and workspace scope, generates an execution envelope proposal, and emits replay-safe semantic evidence.

Natural Language is governance input, not execution authority.

## Why Prompts Are Not Authority

Prompts are ambiguous, user-authored intent expressions. They cannot directly execute, invoke providers, define workspace authority, bypass governance, or bypass validation.

The permanent invariant is:

```text
Natural Language != Execution Authority
```

## Why Semantic Governance Exists

Semantic governance converts intent into explicit bounded structures that downstream validators can inspect. Without this layer, prompt text could be mistaken for permission.

## Why Intent Classification Exists

Intent classification makes the semantic path deterministic and replay-visible. Unknown or ambiguous classification fails closed.

## Why Admissibility Evaluation Exists

Admissibility rejects implicit execution authority, governance bypass, validation bypass, unrestricted shell access, and ambiguous authority escalation before envelope generation.

## Why Envelopes Must Precede Execution

Execution providers receive envelopes, not prompts. Envelopes bind provider identity, authority scope, workspace scope, replay identity, and validation requirements.

## Why Replay-Safe Semantic Lineage Matters

Semantic lineage preserves the original request, replay identity, classification, admissibility, authority mapping, workspace mapping, and envelope proposal status.

## Relationship To Prior Milestones

- `EXECUTION_ENVELOPE_MODEL_V1` defines bounded execution proposals.
- `TRANSPORT_BRIDGE_V1` delivers validated envelopes.
- `PROVIDER_ABSTRACTION_FOUNDATION_V1` keeps providers bounded and replaceable.
- `AGOL_LAYER_SEPARATION_MODEL_V1` separates interaction, governance, execution, validation, and reflection authority.

## Explicit Non-Goals

- Autonomous reasoning.
- Autonomous planning.
- Autonomous execution.
- Orchestration.
- Adaptive routing.
- Retries.
- Fallback logic.
- Provider API integration.
- Runtime execution.
- Transport execution.
- Hidden reasoning chains.
- Self-modifying governance.
