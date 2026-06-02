# RESULT_EVALUATION_ADR_V1

## Status

Accepted.

## Context

`RESULT_RUNTIME_V1` is certified and can capture worker output as `RESULT_ARTIFACT_V1`.

Result capture intentionally does not evaluate quality, approve results, certify results, analyze failures, reflect, self-improve, mutate governance, or mutate replay.

The next boundary is evaluation: a replay-visible assessment of a captured result that remains separate from governance and approval.

## Decision

Define Result Evaluation as a separate future boundary after result capture:

```text
Execution
-> Completion
-> Result
-> Evaluation
```

`RESULT_EVALUATION_ARTIFACT_V1` will record evaluation observations about a captured result and bind those observations to result evidence, canonical chain evidence, evaluator evidence, and replay continuity.

Evaluation may recommend a future improvement proposal, but it may not create, approve, execute, or apply that improvement.

## Rationale

Separating result capture from evaluation prevents semantic collapse:

- result capture records worker output;
- evaluation records observations about that output;
- approval remains explicit human-authorized governance;
- improvement proposal remains a separate governed lifecycle artifact;
- self-improvement remains out of scope.

This preserves replay clarity and avoids granting providers, workers, or evaluators governance authority.

## Consequences

Future runtime work can implement `RESULT_EVALUATION_ARTIFACT_V1` without changing Result Runtime, Completion Runtime, Execution Runtime, or Proposal Approval Runtime.

Evaluation evidence can become an input to future governed proposal creation, but only through explicit proposal lifecycle boundaries.

No actor gains authority to approve, certify, mutate, or self-improve from evaluation.

## Non-Goals

This ADR does not implement:

- Result Evaluation Runtime;
- Result Approval Runtime;
- Result Certification Runtime;
- Reflection Runtime;
- Self-Improvement Runtime;
- Improvement Proposal Runtime;
- governance mutation;
- replay repair;
- execution mutation.

## Final Classification

```text
RESULT_EVALUATION_FOUNDATION_STATUS = READY
```
