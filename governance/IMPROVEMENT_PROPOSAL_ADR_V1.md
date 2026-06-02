# IMPROVEMENT_PROPOSAL_ADR_V1

## Status

Accepted.

## Context

`RESULT_EVALUATION_FOUNDATION_V1` defines evaluation as replay-visible observations about captured results.

Evaluation may recommend improvement, but it intentionally does not create, approve, implement, or apply improvements.

The next boundary is improvement proposal: a replay-visible, chain-bound artifact that can carry evaluation evidence into a future governed approval path.

## Decision

Define Improvement Proposal as a separate future boundary after evaluation:

```text
Execution
-> Completion
-> Result
-> Evaluation
-> Improvement Proposal
```

`IMPROVEMENT_PROPOSAL_ARTIFACT_V1` will record a proposed improvement derived from valid evaluation evidence.

The artifact requires approval before any implementation. It does not authorize implementation, create execution requests, dispatch workers, invoke workers, perform reflection, or apply self-improvement.

## Rationale

Separating evaluation from improvement proposal prevents semantic collapse:

- result captures output;
- evaluation records observations;
- improvement proposal describes a possible change;
- approval remains explicit human-authorized governance;
- implementation remains a future governed execution path.

This preserves replay clarity and avoids giving evaluators, providers, workers, or proposals autonomous mutation authority.

## Consequences

Future runtime work can implement `IMPROVEMENT_PROPOSAL_ARTIFACT_V1` without changing Result Runtime or Result Evaluation semantics.

Improvement proposals can become inputs to future approval boundaries, but cannot skip approval or perform implementation.

No actor gains self-improvement authority from this foundation.

## Non-Goals

This ADR does not implement:

- Improvement Proposal Runtime;
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
IMPROVEMENT_PROPOSAL_FOUNDATION_STATUS = READY
```
