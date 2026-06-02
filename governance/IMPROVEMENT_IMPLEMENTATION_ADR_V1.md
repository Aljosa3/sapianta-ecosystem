# IMPROVEMENT_IMPLEMENTATION_ADR_V1

## Status

Accepted.

## Context

`IMPROVEMENT_APPROVAL_FOUNDATION_V1` defines approval as an explicit human-authorized decision over a reviewed improvement proposal.

Approval may authorize a future implementation path, but it intentionally does not implement, create execution requests, dispatch workers, invoke workers, self-modify, mutate governance, or mutate replay.

The next boundary is implementation planning: a replay-visible plan derived from approved improvement evidence.

## Decision

Define Improvement Implementation Planning as a separate future boundary after improvement approval:

```text
Result
-> Evaluation
-> Improvement Proposal
-> Improvement Review
-> Improvement Approval
-> Implementation Plan
```

`IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` will record a bounded implementation plan for an approved improvement and bind that plan to approval, review, proposal, evaluation, result, canonical chain, and replay evidence.

The plan may prepare a future execution request path. It may not create the execution request, perform implementation, mutate code, dispatch workers, invoke workers, perform self-modification, or mutate governance.

## Rationale

Separating approval from implementation planning prevents semantic collapse:

- approval records the human-authorized decision;
- implementation plan translates that decision into bounded future steps;
- execution request remains a separate governed runtime boundary;
- actual code change remains future governed execution output.

This preserves replay clarity and avoids granting approvals, plans, providers, workers, or AiGOL autonomous code mutation authority.

## Consequences

Future runtime work can implement `IMPROVEMENT_IMPLEMENTATION_PLAN_ARTIFACT_V1` without changing Improvement Approval, Improvement Review, Improvement Proposal, Result Evaluation, or Result Runtime semantics.

Implementation plans can become inputs to future execution request foundations or runtimes, but cannot skip execution request governance.

No actor gains self-application, self-modification, or self-improvement authority from this foundation.

## Non-Goals

This ADR does not implement:

- Improvement Implementation Planning Runtime;
- execution request creation;
- code mutation;
- configuration mutation;
- worker dispatch;
- worker invocation;
- reflection;
- self-modification;
- self-improvement;
- governance mutation;
- replay repair.

## Final Classification

```text
IMPROVEMENT_IMPLEMENTATION_FOUNDATION_STATUS = READY
```
