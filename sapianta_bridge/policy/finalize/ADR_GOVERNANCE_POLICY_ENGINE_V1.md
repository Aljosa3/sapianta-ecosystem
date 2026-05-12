# ADR: GOVERNANCE_POLICY_ENGINE_V1

## Context

SAPIANTA requires constitutional admissibility classification before any execution authorization or bounded autonomy layer can exist.

Reflection is advisory, approval is human-governed, and transport is bounded. A policy layer is needed to classify advisory proposals, approval candidates, and governance requests into deterministic admissibility and escalation states without granting authority.

## Decision

Introduce a deterministic classification-only governance policy layer with:

- Admissibility classes.
- Escalation classes.
- Forbidden capability detection.
- Replay-safe policy evidence.
- No execution authority.

Policy records what is allowed, restricted, escalated, or blocked. It does not approve, execute, invoke transport, invoke Codex, or mutate governance.

## Consequences

Positive:

- Governance admissibility becomes explicit.
- Forbidden capabilities become formally blocked.
- Escalation semantics become deterministic.
- Policy evidence becomes replay-visible.
- Future bounded autonomy becomes safer.

Tradeoffs:

- Additional governance overhead.
- Slower progression toward autonomy.
- Stricter fail-closed behavior.
- Increased architectural complexity.

## Explicit Non-Goals

- Execution.
- Automatic approval.
- Bounded autonomy.
- Execution authorization.
- Recursive orchestration.
- Policy-triggered execution.
- Runtime authority escalation.
