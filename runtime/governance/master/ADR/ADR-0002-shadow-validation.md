# ADR-0002: Shadow Validation

## STATUS

Accepted as dormant architectural foundation.

## CONTEXT

SAPIANTA needs a way to reason about validation without making validation authoritative at runtime. Immediate enforcement would create risk before replay behavior, approval semantics, and governance boundaries are fully proven.

Shadow validation preserves the distinction between observing decisions and controlling decisions.

ACTIVE has no runtime meaning.

## DECISION

Use shadow validation as an observational concept. It may describe how decisions could be evaluated, explained, or compared in future governance work, but it does not block, approve, mutate, or execute runtime behavior.

Governance remains dormant, replay-safe, and observational only.

## CONSEQUENCES

Shadow validation supports AI Decision Validator positioning by making validation understandable without claiming active enforcement. Future enforcement requires separate ADRs, tests, milestones, and human approval.

## NON-GOALS

- Runtime blocking
- Runtime approval execution
- Policy enforcement
- Automatic validation activation
- Governance arbitration
