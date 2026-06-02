# TRADING_DECISION_VALIDATION_TEST_FIXTURES_V1

## Status

Review-only fixture architecture.

No worker implementation, strategy implementation, exchange integration, broker integration, order placement, live trading, or profitability claim is introduced by these fixtures.

## Final Classification

```text
TRADING_DECISION_VALIDATION_TEST_FIXTURES_STATUS = CERTIFIED
```

## Purpose

Define canonical validation fixtures and evidence scenarios for future Trading Decision Validation worker testing.

The fixtures are replay-visible scenario definitions, not runtime tests and not trading recommendations.

## Fixture Set

Canonical fixture categories:

- valid trading decision request;
- insufficient evidence;
- incomplete portfolio context;
- unacceptable risk;
- policy violation;
- human review escalation;
- learning review escalation;
- fail-closed replay integrity;
- fail-closed authority violation;
- optional advisory evidence.

## Direct Answers

### 1. Which minimal fixture represents a valid trading decision request?

Fixture:

```text
TDV_FIXTURE_VALID_MINIMAL_REVIEWABLE_REQUEST
```

Expected outcome:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

Required properties:

- Trading Decision Request present;
- Market Evidence present;
- Portfolio Context present where required;
- Risk Context present;
- Strategy Context present;
- Policy Constraint Context present;
- canonical chain continuity preserved;
- evidence hashes present;
- replay visible;
- no-live-execution flags false;
- human review required.

### 2. Which fixture represents insufficient evidence?

Fixture:

```text
TDV_FIXTURE_INSUFFICIENT_MARKET_EVIDENCE
```

Expected outcome:

```text
INSUFFICIENT_EVIDENCE
```

Missing or invalid evidence:

- missing Market Evidence;
- stale Market Evidence;
- missing market evidence hash;
- missing market source identity.

### 3. Which fixture represents incomplete portfolio context?

Fixture:

```text
TDV_FIXTURE_INCOMPLETE_PORTFOLIO_CONTEXT
```

Expected outcome:

```text
INCOMPLETE_PORTFOLIO_CONTEXT
```

Missing or invalid evidence:

- missing portfolio scope;
- missing position context hash;
- missing exposure context hash;
- missing hypothetical-only marker;
- missing portfolio mutation false flag.

### 4. Which fixture represents unacceptable risk?

Fixture:

```text
TDV_FIXTURE_UNACCEPTABLE_RISK
```

Expected outcome:

```text
UNACCEPTABLE_RISK
```

Risk condition:

- failed exposure check;
- failed concentration check;
- failed liquidity check;
- failed volatility check;
- failed drawdown check;
- ambiguous or missing risk rationale.

### 5. Which fixture represents policy violation?

Fixture:

```text
TDV_FIXTURE_POLICY_VIOLATION
```

Expected outcome:

```text
POLICY_VIOLATION
```

Policy violation examples:

- prohibited instrument;
- prohibited venue;
- financial performance claim;
- strategy deployment claim;
- missing human review requirement.

### 6. Which fixture requires human review escalation?

Fixture:

```text
TDV_FIXTURE_HUMAN_REVIEW_ESCALATION
```

Expected outcome:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

Escalation category:

```text
HUMAN_REVIEW_REQUIRED
```

### 7. Which fixture requires learning review escalation?

Fixture:

```text
TDV_FIXTURE_LEARNING_REVIEW_ESCALATION
```

Expected outcome:

```text
LEARNING_REVIEW
```

Escalation trigger:

- proposed evidence requirement improvement;
- proposed risk threshold review;
- proposed replay model refinement;
- proposed worker quality improvement.

Learning feedback remains advisory and cannot self-apply.

### 8. Which fixture should fail closed?

Fail-closed fixtures:

```text
TDV_FIXTURE_REPLAY_HASH_MISMATCH
TDV_FIXTURE_CHAIN_CONTINUITY_FAILURE
TDV_FIXTURE_BROKER_INVOCATION_DETECTED
TDV_FIXTURE_ORDER_PLACEMENT_DETECTED
```

Expected outcome:

```text
FAILED_CLOSED
```

### 9. Which evidence fields are mandatory in every fixture?

Mandatory fields:

- `fixture_id`;
- `fixture_category`;
- `expected_validation_result`;
- `canonical_chain_id`;
- `trading_decision_id`;
- `decision_request_reference`;
- `market_evidence_reference`;
- `portfolio_context_reference`;
- `risk_context_reference`;
- `strategy_context_reference`;
- `policy_constraint_reference`;
- `replay_reference`;
- `replay_visible`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;
- `live_trading_performed`;
- `portfolio_mutated`;
- `strategy_deployed`;
- `financial_claim_made`.

### 10. Which evidence fields are optional?

Optional fields:

- `alternative_scenario_references`;
- `additional_market_data_references`;
- `historical_simulation_reference`;
- `rejected_alternative_recommendations`;
- `explanation_reference`;
- `learning_feedback_reference`;
- `operator_notes_reference`.

### 11. What replay evidence should exist for every fixture?

Every fixture should include replay evidence for:

- fixture declaration;
- decision request;
- market evidence;
- portfolio context where required;
- risk context;
- strategy context;
- policy constraints;
- expected validation outcome;
- expected rejection or escalation reason where applicable;
- no-live-execution flags.

### 12. How should fixtures be organized for future worker testing?

Future worker fixtures should be organized by:

```text
governance/trading/fixtures/<fixture_category>/<fixture_id>.json
```

Recommended top-level categories:

- `valid`;
- `insufficient_evidence`;
- `portfolio_context`;
- `risk`;
- `policy_violation`;
- `escalation`;
- `learning`;
- `fail_closed`;
- `advisory`.

## Boundary

This fixture architecture does not implement fixture files, worker code, strategy logic, broker integration, exchange integration, live trading, order placement, or financial claims.
