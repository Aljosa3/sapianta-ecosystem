# TRADING_DECISION_ESCALATION_MODEL_V1

## Status

Review-only escalation model.

## Purpose

Define when a Trading Decision Validation outcome must be escalated to human review.

Escalation is review-only. It is not execution authority.

## Escalation Categories

### HUMAN_REVIEW_REQUIRED

Required whenever validation returns:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

Meaning:

The recommendation has enough evidence for human review, but no trade or execution is authorized.

### MATERIAL_RISK_REVIEW

Required when evidence is complete but risk remains material, complex, or policy-sensitive.

Examples:

- exposure changes;
- concentration changes;
- volatile market context;
- liquidity sensitivity;
- drawdown sensitivity.

### POLICY_REVIEW

Required when a decision depends on policy interpretation.

Examples:

- policy constraint is ambiguous;
- asset class classification is unclear;
- venue or instrument status is unclear;
- evidence freshness policy needs interpretation.

### PORTFOLIO_CONTEXT_REVIEW

Required when the decision affects portfolio exposure, allocation, concentration, or hypothetical versus real-state interpretation.

### LEARNING_REVIEW

Required when learning feedback proposes:

- policy refinement;
- evidence requirement changes;
- risk threshold review;
- worker quality changes;
- replay model refinements.

### FAIL_CLOSED_REVIEW

Required when validation fails closed due to replay, integrity, authority, or chain continuity concerns.

The review may inspect evidence, but must not repair replay through this model.

## Non-Escalation Outcomes

The following outcomes do not require human review before rejection is recorded:

- clear insufficient evidence;
- clear out-of-scope request;
- clear prohibited execution request;
- clear broker or exchange invocation attempt;
- clear financial performance claim.

Operators may still review rejected outcomes for learning or audit purposes.

## Escalation Evidence

Escalation must record:

- escalation category;
- source validation result;
- evidence references;
- reason;
- reason hash;
- canonical chain id;
- replay reference;
- human review required flag;
- no-live-execution flags.

## Escalation Boundary

Escalation does not:

- approve a trade;
- authorize broker invocation;
- authorize exchange invocation;
- create an order;
- create a live execution request;
- mutate portfolio state;
- change policy.

## Human Review Outcome Boundary

Human review may decide how to proceed inside future governed workflows.

This acceptance model does not define live execution workflows and does not allow human review to bypass AiGOL Core governance.
