# TRADING_DECISION_FIXTURE_MODEL_V1

## Status

Review-only fixture model.

## Fixture Identity

Each fixture must define:

- `fixture_id`;
- `fixture_version`;
- `fixture_category`;
- `fixture_purpose`;
- `canonical_chain_id`;
- `expected_validation_result`;
- `expected_rejection_category`;
- `expected_escalation_category`;
- `expected_fail_closed`;
- `replay_visible`.

## Fixture Categories

### VALID

Fixture:

```text
TDV_FIXTURE_VALID_MINIMAL_REVIEWABLE_REQUEST
```

Purpose:

Baseline valid decision-validation request for human review.

Expected:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

### INSUFFICIENT_EVIDENCE

Fixture:

```text
TDV_FIXTURE_INSUFFICIENT_MARKET_EVIDENCE
```

Purpose:

Confirm missing or stale mandatory evidence rejects validation.

Expected:

```text
INSUFFICIENT_EVIDENCE
```

### INCOMPLETE_PORTFOLIO_CONTEXT

Fixture:

```text
TDV_FIXTURE_INCOMPLETE_PORTFOLIO_CONTEXT
```

Purpose:

Confirm portfolio-aware validation rejects incomplete portfolio context.

Expected:

```text
INCOMPLETE_PORTFOLIO_CONTEXT
```

### UNACCEPTABLE_RISK

Fixture:

```text
TDV_FIXTURE_UNACCEPTABLE_RISK
```

Purpose:

Confirm prohibited or unbounded risk rejects validation.

Expected:

```text
UNACCEPTABLE_RISK
```

### POLICY_VIOLATION

Fixture:

```text
TDV_FIXTURE_POLICY_VIOLATION
```

Purpose:

Confirm policy violation rejects validation.

Expected:

```text
POLICY_VIOLATION
```

### HUMAN_REVIEW_ESCALATION

Fixture:

```text
TDV_FIXTURE_HUMAN_REVIEW_ESCALATION
```

Purpose:

Confirm admissible recommendations require human review.

Expected:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
HUMAN_REVIEW_REQUIRED
```

### LEARNING_REVIEW_ESCALATION

Fixture:

```text
TDV_FIXTURE_LEARNING_REVIEW_ESCALATION
```

Purpose:

Confirm learning recommendations escalate without self-application.

Expected:

```text
LEARNING_REVIEW
```

### FAIL_CLOSED_REPLAY_INTEGRITY

Fixture:

```text
TDV_FIXTURE_REPLAY_HASH_MISMATCH
```

Purpose:

Confirm replay corruption fails closed.

Expected:

```text
FAILED_CLOSED
```

### FAIL_CLOSED_AUTHORITY

Fixture:

```text
TDV_FIXTURE_BROKER_INVOCATION_DETECTED
```

Purpose:

Confirm forbidden authority markers fail closed.

Expected:

```text
FAILED_CLOSED
```

## Mandatory Evidence Fields

Every fixture must include:

- `trading_decision_id`;
- `canonical_chain_id`;
- `decision_request_reference`;
- `decision_request_hash`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `risk_context_reference`;
- `risk_context_hash`;
- `strategy_context_reference`;
- `strategy_context_hash`;
- `policy_constraint_reference`;
- `policy_constraint_hash`;
- `replay_reference`;
- `replay_visible`;
- `expected_validation_result`.

Portfolio-aware fixtures must include:

- `portfolio_context_reference`;
- `portfolio_context_hash`;
- `hypothetical_only`;
- `portfolio_mutated`.

## Required False Flags

Every fixture must record:

```text
broker_invoked = false
exchange_invoked = false
order_placed = false
live_trading_performed = false
portfolio_mutated = false
strategy_deployed = false
financial_claim_made = false
```

Fail-closed authority fixtures may intentionally set one forbidden flag to true as the fixture trigger, with expected result:

```text
FAILED_CLOSED
```

## Optional Evidence Fields

Optional fields:

- `alternative_scenario_references`;
- `additional_market_data_references`;
- `historical_simulation_reference`;
- `explanation_reference`;
- `learning_feedback_reference`;
- `operator_notes_reference`.

Optional evidence cannot satisfy mandatory evidence requirements.
