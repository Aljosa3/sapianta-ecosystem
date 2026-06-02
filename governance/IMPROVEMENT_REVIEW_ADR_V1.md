# IMPROVEMENT_REVIEW_ADR_V1

## Status

Accepted.

## Context

`IMPROVEMENT_PROPOSAL_FOUNDATION_V1` defines improvement proposals as replay-visible proposed changes derived from result evaluation evidence.

Improvement proposals intentionally do not approve, implement, execute, dispatch, invoke, reflect, self-improve, mutate governance, or mutate replay.

The next boundary is review: a replay-visible assessment of an improvement proposal before any explicit approval decision.

## Decision

Define Improvement Review as a separate future boundary after improvement proposal creation:

```text
Execution
-> Completion
-> Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
```

`IMPROVEMENT_REVIEW_ARTIFACT_V1` will record review findings about an improvement proposal and bind those findings to proposal evidence, evaluation evidence, result evidence, canonical chain evidence, and replay continuity.

Review may recommend approval or identify gaps. It may not approve, reject, implement, create execution requests, dispatch workers, invoke workers, perform reflection, or apply self-improvement.

## Rationale

Separating improvement proposal from review prevents semantic collapse:

- proposal describes a possible change;
- review assesses proposal evidence and readiness;
- approval remains explicit human-authorized governance;
- implementation remains a future governed execution path.

This preserves replay clarity and avoids granting reviewers, providers, workers, or review artifacts autonomous decision or mutation authority.

## Consequences

Future runtime work can implement `IMPROVEMENT_REVIEW_ARTIFACT_V1` without changing Improvement Proposal, Result Evaluation, or Result Runtime semantics.

Review evidence can become an input to future approval boundaries, but cannot skip approval or perform implementation.

No actor gains approval, implementation, or self-improvement authority from this foundation.

## Non-Goals

This ADR does not implement:

- Improvement Review Runtime;
- approval;
- implementation;
- worker dispatch;
- worker invocation;
- reflection;
- self-improvement;
- governance mutation;
- replay repair.

## Final Classification

```text
IMPROVEMENT_REVIEW_FOUNDATION_STATUS = READY
```
