# IMPROVEMENT_APPROVAL_ADR_V1

## Status

Accepted.

## Context

`IMPROVEMENT_REVIEW_FOUNDATION_V1` defines review as replay-visible assessment of an improvement proposal.

Review may recommend approval or identify gaps, but it intentionally does not approve, reject, implement, dispatch, invoke, reflect, self-improve, mutate governance, or mutate replay.

The next boundary is approval: an explicit human-authorized decision over a reviewed improvement proposal.

## Decision

Define Improvement Approval as a separate future boundary after improvement review:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
```

`IMPROVEMENT_APPROVAL_ARTIFACT_V1` will record an explicit human-authorized approval or rejection decision and bind that decision to review, proposal, evaluation, result, canonical chain, and replay evidence.

Approval may authorize a future implementation path when the decision is `APPROVED`. It may not implement, create execution requests, dispatch workers, invoke workers, perform self-modification, or mutate governance.

## Rationale

Separating review from approval prevents semantic collapse:

- proposal describes a possible change;
- review assesses evidence and readiness;
- approval records a human-authorized decision;
- implementation remains a separate future governed execution path.

This preserves replay clarity and avoids giving AiGOL, providers, workers, reviewers, or approval artifacts autonomous implementation or governance mutation authority.

## Consequences

Future runtime work can implement `IMPROVEMENT_APPROVAL_ARTIFACT_V1` without changing Improvement Review, Improvement Proposal, Result Evaluation, or Result Runtime semantics.

Approved improvement proposals can become inputs to future implementation foundations or runtimes, but approval cannot skip implementation governance.

Rejected improvement proposals remain replay-visible and non-executable.

## Non-Goals

This ADR does not implement:

- Improvement Approval Runtime;
- implementation;
- execution request creation;
- worker dispatch;
- worker invocation;
- reflection;
- self-modification;
- self-improvement;
- governance mutation;
- replay repair.

## Final Classification

```text
IMPROVEMENT_APPROVAL_FOUNDATION_STATUS = READY
```
