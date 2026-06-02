# TRADING_DECISION_VALIDATION_ACCEPTANCE_CRITERIA_V1

## Status

Review-only acceptance criteria.

No strategy implementation, live trading, order placement, profitability claim, broker integration, or exchange integration is introduced by these criteria.

## Final Classification

```text
TRADING_DECISION_VALIDATION_ACCEPTANCE_STATUS = CERTIFIED
```

## Purpose

Define objective acceptance criteria for Trading Domain decision validation.

The criteria determine whether a trading decision request may be evaluated, rejected, failed closed, or escalated to human review.

They do not authorize execution.

## Direct Answers

### 1. What minimum evidence is required before a trading decision may be evaluated?

Mandatory minimum evidence:

- Trading Decision Request;
- Market Evidence;
- Portfolio Context;
- Risk Context;
- Strategy Context;
- Policy Constraint Context;
- Replay Context;
- canonical chain id;
- no-live-execution flags;
- human review requirement.

All required evidence must be replay-visible and hashable.

### 2. What constitutes insufficient evidence?

Insufficient evidence exists when any mandatory evidence is missing, stale, unhashable, not replay-visible, not chain-linked, or internally inconsistent.

Insufficient evidence also exists when a worker report references evidence outside the canonical chain without an explicit governed reference.

### 3. What constitutes incomplete portfolio context?

Incomplete portfolio context exists when the request requires portfolio awareness but lacks:

- portfolio scope;
- position context hash;
- cash or margin context hash where relevant;
- exposure context hash;
- hypothetical-only marker;
- portfolio mutation false flag.

Because this foundation does not authorize live portfolio state mutation, portfolio context may be hypothetical, but it must be explicit.

### 4. What constitutes unacceptable risk?

Unacceptable risk exists when risk evidence indicates violation of configured trading policy constraints or when risk cannot be bounded enough for human review.

Examples:

- exposure check fails;
- concentration check fails;
- liquidity check fails;
- volatility check fails;
- drawdown check fails;
- prohibited instrument or venue appears;
- risk rationale is missing;
- downside scenario is ambiguous.

Concrete thresholds are not defined here and must be supplied by a future trading policy milestone.

### 5. What constitutes policy violation?

Policy violation exists when the request, evidence, worker output, or recommendation conflicts with an active trading policy constraint.

Policy violation includes:

- out-of-scope asset class;
- prohibited instrument;
- prohibited venue;
- missing human review;
- missing replay visibility;
- attempted broker invocation;
- attempted exchange invocation;
- attempted order placement;
- financial performance claim;
- strategy deployment claim.

### 6. What constitutes a valid decision recommendation?

A valid decision recommendation:

- uses an allowed validation result;
- references all required evidence and hashes;
- preserves canonical chain continuity;
- states a validation reason and reason hash;
- identifies mandatory human review;
- records no-live-execution flags as false;
- avoids financial performance claims;
- is replay-visible.

The strongest positive result is:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

This is not execution authority.

### 7. What constitutes a rejected recommendation?

A rejected recommendation is a replay-visible non-admissible validation outcome.

Rejection categories include:

- `INSUFFICIENT_EVIDENCE`;
- `UNACCEPTABLE_RISK`;
- `POLICY_VIOLATION`;
- `OUT_OF_SCOPE`;
- `FAILED_CLOSED`;
- `REJECTED_BY_GOVERNANCE`.

### 8. What constitutes escalation to human review?

Human review is required when:

- validation result is `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- evidence is complete but risk remains material;
- policy requires human judgment;
- the decision affects portfolio exposure;
- a learning recommendation proposes policy or threshold review;
- explanation confidence is low but evidence is sufficient;
- any future transition toward action is contemplated.

Escalation is review-only and does not authorize trading.

### 9. Which criteria are mandatory?

Mandatory criteria:

- required evidence present;
- required evidence hashable;
- replay visible;
- canonical chain continuous;
- market evidence freshness status present;
- portfolio context complete where required;
- risk context complete;
- policy constraints present;
- no-live-execution flags false;
- no financial claim;
- human review requirement present;
- allowed validation result only.

### 10. Which criteria are advisory?

Advisory criteria:

- explanation quality;
- scenario coverage breadth;
- market data source diversity;
- confidence narration;
- alternative decision comparison;
- learning improvement suggestion;
- operator readability;
- audit package clarity.

Advisory criteria may improve review quality but must not override mandatory rejection or fail-closed conditions.

## Acceptance Outcomes

Allowed outcomes:

- `ACCEPTED_FOR_VALIDATION`;
- `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- `REJECTED_BY_GOVERNANCE`;
- `FAILED_CLOSED`;
- `INSUFFICIENT_EVIDENCE`;
- `UNACCEPTABLE_RISK`;
- `POLICY_VIOLATION`;
- `OUT_OF_SCOPE`;
- `SIMULATION_ONLY`.

## Boundary

Acceptance criteria do not create:

- strategy logic;
- live trading;
- order placement;
- broker integration;
- exchange integration;
- execution requests for live trading;
- profitability claims.
