# PROVIDER_WORKER_ADR_V1

## Status

Accepted.

## Context

The provider layer is certified as substitutable and proposal-only.

The worker layer is certified as execution-only and authorization-dependent.

The question is whether provider proposals can safely approach worker domains
without obtaining execution authority.

## Decision

Certify provider-worker domain compatibility only through:

```text
Provider
-> Proposal
-> Governance Review
-> Authorization Decision
-> Worker Request
-> Worker Execution
-> Replay
```

Provider proposals may be interpreted by governance, but may not invoke,
dispatch, authorize, or mutate workers.

## Rationale

Existing artifacts already separate:

- proposal evidence
- governance admissibility
- authorization evidence
- worker execution request
- worker result evidence
- replay evidence

This separation preserves:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```

## Consequences

Provider-to-worker compatibility is certified.

Direct provider-to-worker execution remains forbidden.

Every worker domain requires governance review, authorization, replay
visibility, and fail-closed handling before execution can occur.

## Non-Goals

This ADR does not implement:

- worker runtime
- execution engine
- authorization engine
- governance activation
- orchestration
- planning
- reflection
- dispatch
- autonomous execution
- runtime mutation

## Certification

PROVIDER_WORKER_COMPATIBILITY_STATUS = CERTIFIED
