# ADR: Executor Adapter Runtime v1

## Context

AiGOL now has provider abstraction and execution envelopes. The next bounded step is runtime delivery from a validated envelope into an explicit provider adapter, returning a normalized result and replay-safe evidence.

This is the first operational bridge substrate milestone, but it remains local, deterministic, and non-autonomous.

## Decision

Introduce `EXECUTOR_ADAPTER_RUNTIME_V1`:

- validate execution envelope before runtime;
- create deterministic runtime binding;
- enforce provider identity match;
- guard against authority escalation and mutation;
- execute only inert or deterministic adapters;
- wrap normalized results;
- produce replay-safe runtime evidence.

Executor runtime is bounded adapter delivery, not orchestration.

## Why Runtime Delivery Is Introduced Now

Provider abstraction and envelope validation exist, so the system can safely model envelope-to-adapter delivery without adding real provider calls or autonomous control.

## Why Adapters Remain Bounded

Adapters cannot self-authorize, expand authority, mutate governance, mutate replay state, bypass validation, enqueue tasks, or retry silently.

## Why Real Provider Calls Are Excluded

Real provider calls introduce network behavior, provider-specific failure modes, credentials, scheduling, and external state. This milestone only validates the bounded runtime substrate.

## Why Routing Is Excluded

Routing would imply provider selection intelligence and scheduling authority. This milestone binds one explicit provider adapter to one validated envelope.

## Why Envelope Validation Comes First

The envelope defines authority, workspace, replay identity, provider identity, and validation requirements. Runtime delivery without envelope validation would create hidden authority.

## Relationship To Prior Milestones

- `PROVIDER_ABSTRACTION_FOUNDATION_V1` defines provider contracts and normalized results.
- `EXECUTION_ENVELOPE_MODEL_V1` defines bounded transport authority.
- `AGOL_LAYER_SEPARATION_MODEL_V1` separates execution from governance and validation authority.
- `GOVERNANCE_WORKTREE_HYGIENE_V1` protects runtime evidence from transient artifact pollution.

## Consequences

Positive:

- Valid envelopes can reach deterministic adapters.
- Invalid envelopes are blocked.
- Provider identity is enforced.
- Runtime evidence is replay-safe.
- No routing, fallback, retry, or external execution is introduced.

Tradeoffs:

- No real Codex or Claude execution exists yet.
- No full bridge transport exists yet.
- Provider selection remains caller-explicit.

## Explicit Non-Goals

- Provider routing.
- Autonomous orchestration.
- Dynamic scheduling.
- Provider optimization.
- Fallback logic.
- Retry logic.
- Hidden execution.
- Real provider API integration.
- Full bridge transport.
- Production execution.
