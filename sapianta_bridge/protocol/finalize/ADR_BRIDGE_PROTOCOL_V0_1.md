# ADR: BRIDGE_PROTOCOL_V0_1

## Context

SAPIANTA requires governed AI coordination artifacts before any bridge runtime, subprocess transport, or orchestration layer exists. Protocol-first architecture was chosen to prevent execution behavior from appearing before deterministic evidence, lineage, lifecycle states, and validation contracts are stable.

## Decision

Formalize canonical schemas, lifecycle states, lineage rules, replay-safe hashing, validation contracts, and evidence envelopes as `SAPIANTA CODEX BRIDGE PROTOCOL v0.1` before implementing bridge runtime transport.

The protocol is finalized as a governance substrate only. It does not execute Codex, invoke subprocesses, automate reflection, recurse, approve work, merge work, push work, or mutate governance.

## Consequences

Positive:

- Prevents artifact drift.
- Prevents hidden execution states.
- Stabilizes future orchestration.
- Enables replay-safe governance.
- Makes lifecycle and lineage explicit before runtime transport.

Tradeoffs:

- Slower initial execution progress.
- Additional governance overhead.
- More explicit protocol constraints.
- Future transport must conform to the finalized protocol instead of defining its own artifact shape.

## Explicit Non-Goals

- Execution.
- Autonomy.
- Orchestration.
- Recursive planning.
- Bridge listener implementation.
- Codex subprocess invocation.
- Runtime authority.

