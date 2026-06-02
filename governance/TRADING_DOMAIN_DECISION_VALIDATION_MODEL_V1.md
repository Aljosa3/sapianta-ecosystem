# TRADING_DOMAIN_DECISION_VALIDATION_MODEL_V1

## Status

Review-only decision-validation architecture.

No broker integration, exchange integration, order placement, live trading, strategy implementation, or financial performance claim is introduced by this model.

## Final Classification

```text
TRADING_DOMAIN_DECISION_VALIDATION_STATUS = CERTIFIED
```

## Purpose

Define the governed decision-validation model for the Trading Domain.

The model evaluates whether a trading-related recommendation is admissible for human review under available evidence, risk constraints, replay visibility, and AiGOL Core governance.

It does not authorize or execute trades.

## Direct Answers

### 1. What is a Trading Decision Request?

A Trading Decision Request is a replay-visible proposal asking AiGOL to validate a trading-related recommendation.

It may ask whether a proposed action, strategy signal, portfolio adjustment, or rejection should be considered admissible for human review.

It is not:

- an order;
- an order intent;
- a broker instruction;
- an exchange instruction;
- a financial recommendation;
- execution authority.

### 2. What evidence must accompany a Trading Decision Request?

Minimum evidence:

- Market Evidence;
- Portfolio Context;
- Risk Context;
- Strategy Context;
- Policy Constraint Context;
- Human Review Requirement;
- Replay Context;
- no-live-execution flags.

Each evidence object must be replay-visible, hashable, and linked to the same canonical chain.

### 3. What validations must occur?

Required validations:

- request completeness validation;
- canonical chain continuity validation;
- market evidence freshness validation;
- market evidence source validation;
- portfolio context validation;
- risk context validation;
- strategy context validation;
- policy constraint validation;
- prohibited action validation;
- replay visibility validation;
- live execution absence validation;
- human review requirement validation.

### 4. What constitutes insufficient evidence?

Insufficient evidence exists when:

- market evidence is missing;
- market evidence is stale beyond policy;
- market source identity is missing;
- portfolio context is missing where required;
- risk context is missing or incomplete;
- strategy context is unsupported by evidence;
- policy constraints are missing;
- evidence hashes are absent or mismatched;
- canonical chain identity is absent;
- replay visibility is absent.

### 5. What constitutes unacceptable risk?

Unacceptable risk exists when the proposed decision violates configured domain constraints.

Examples:

- exposure exceeds limit;
- concentration exceeds limit;
- liquidity is insufficient;
- volatility exceeds policy;
- drawdown constraint is violated;
- prohibited instrument or venue is involved;
- required human review is absent;
- risk context is ambiguous;
- downside scenario is unbounded or unexplained.

This model does not define concrete risk thresholds. Thresholds belong to a future trading policy milestone.

### 6. What constitutes a valid decision recommendation?

A valid decision recommendation is a validation output that:

- is replay-visible;
- references all required evidence and hashes;
- preserves canonical chain continuity;
- states a validation result;
- states a reason;
- identifies required human review;
- confirms no broker invocation;
- confirms no exchange invocation;
- confirms no order placement;
- does not claim profitability or financial suitability.

Valid result classes:

- `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- `REJECTED_BY_GOVERNANCE`;
- `FAILED_CLOSED`;
- `INSUFFICIENT_EVIDENCE`;
- `UNACCEPTABLE_RISK`;
- `OUT_OF_SCOPE`;
- `SIMULATION_ONLY`.

### 7. What constitutes a rejected recommendation?

A rejected recommendation is a governed validation output with result:

```text
REJECTED_BY_GOVERNANCE
```

or another non-admissible result class.

Rejection is required when:

- evidence is insufficient;
- risk is unacceptable;
- request is out of scope;
- live execution is attempted;
- broker or exchange invocation is detected;
- order placement is attempted;
- replay is corrupt or incomplete;
- human authorization is ambiguous.

### 8. Which workers participate?

Candidate workers:

- Market Data Worker;
- Market Evidence Normalization Worker;
- Portfolio Worker;
- Strategy Evaluation Worker;
- Trading Risk Analysis Worker;
- Compliance Constraint Worker;
- Decision Explanation Worker;
- Trading Replay Inspector Worker.

All workers produce validation evidence only.

### 9. What replay evidence must be recorded?

Replay must record:

- trading decision request artifact;
- market evidence artifact;
- portfolio context artifact;
- risk context artifact;
- strategy context artifact;
- policy constraint artifact;
- validation result artifact;
- worker evidence references and hashes;
- validation reason hash;
- fail-closed reason where applicable;
- canonical chain id;
- no-live-execution flags.

### 10. How does learning attach to decision outcomes?

Governed learning may attach to decision outcomes as feedback evidence.

Learning may propose:

- evidence requirement improvements;
- policy clarification requests;
- risk threshold review requests;
- worker quality improvements;
- replay completeness improvements;
- explanation quality improvements.

Learning may not:

- change policy autonomously;
- deploy strategies;
- authorize trades;
- place orders;
- convert validation outcomes into execution authority.

## Candidate Decision Lifecycle

```text
TRADING_DECISION_REQUESTED
TRADING_EVIDENCE_COLLECTED
TRADING_EVIDENCE_NORMALIZED
PORTFOLIO_CONTEXT_VALIDATED
STRATEGY_CONTEXT_EVALUATED
RISK_CONTEXT_ANALYZED
POLICY_CONSTRAINTS_VALIDATED
TRADING_DECISION_VALIDATED
HUMAN_REVIEW_REQUIRED
TRADING_DECISION_RECORDED
TRADING_LEARNING_FEEDBACK_ATTACHED
```

## Boundary

This model is decision-validation architecture only.

It creates no runtime, no strategy implementation, no worker implementation, no broker connection, no exchange connection, no order placement path, and no financial claim.
