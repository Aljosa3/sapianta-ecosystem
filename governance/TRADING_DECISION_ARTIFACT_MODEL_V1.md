# TRADING_DECISION_ARTIFACT_MODEL_V1

## Status

Review-only artifact model.

## Artifact Purpose

Define the replay-visible artifact families required for Trading Domain decision validation.

No runtime schema or implementation is introduced by this artifact.

## Artifact Family

### TRADING_DECISION_REQUEST_ARTIFACT_V1

Purpose:

Capture the proposed trading-related decision to validate.

Required fields:

- `artifact_type`;
- `trading_decision_id`;
- `canonical_chain_id`;
- `requested_by`;
- `requested_at`;
- `decision_type`;
- `decision_summary`;
- `instrument_scope`;
- `time_horizon`;
- `strategy_context_reference`;
- `strategy_context_hash`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `portfolio_context_reference`;
- `portfolio_context_hash`;
- `risk_context_reference`;
- `risk_context_hash`;
- `policy_constraint_reference`;
- `policy_constraint_hash`;
- `human_review_required`;
- `replay_reference`;
- `replay_visible`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;
- `live_trading_performed`;
- `artifact_hash`.

### MARKET_EVIDENCE_ARTIFACT_V1

Purpose:

Capture market context required for validation.

Required fields:

- `market_evidence_id`;
- `canonical_chain_id`;
- `data_source`;
- `source_timestamp`;
- `observed_at`;
- `freshness_status`;
- `instrument_identifiers`;
- `market_snapshot_hash`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

### PORTFOLIO_CONTEXT_ARTIFACT_V1

Purpose:

Capture current or hypothetical portfolio context.

Required fields:

- `portfolio_context_id`;
- `canonical_chain_id`;
- `portfolio_scope`;
- `position_context_hash`;
- `cash_or_margin_context_hash`;
- `exposure_context_hash`;
- `hypothetical_only`;
- `portfolio_mutated`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

### STRATEGY_CONTEXT_ARTIFACT_V1

Purpose:

Capture strategy claim or signal context without implementing a strategy.

Required fields:

- `strategy_context_id`;
- `canonical_chain_id`;
- `strategy_claim_summary`;
- `signal_evidence_reference`;
- `signal_evidence_hash`;
- `strategy_implemented`;
- `strategy_deployed`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

### RISK_CONTEXT_ARTIFACT_V1

Purpose:

Capture risk analysis context.

Required fields:

- `risk_context_id`;
- `canonical_chain_id`;
- `risk_policy_reference`;
- `risk_policy_hash`;
- `exposure_check_status`;
- `concentration_check_status`;
- `liquidity_check_status`;
- `volatility_check_status`;
- `drawdown_check_status`;
- `risk_result`;
- `risk_reason_hash`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

### TRADING_DECISION_VALIDATION_ARTIFACT_V1

Purpose:

Capture governed validation result.

Required fields:

- `trading_validation_id`;
- `trading_decision_id`;
- `canonical_chain_id`;
- `decision_request_reference`;
- `decision_request_hash`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `portfolio_context_reference`;
- `portfolio_context_hash`;
- `strategy_context_reference`;
- `strategy_context_hash`;
- `risk_context_reference`;
- `risk_context_hash`;
- `policy_constraint_reference`;
- `policy_constraint_hash`;
- `validation_result`;
- `validation_reason`;
- `validation_reason_hash`;
- `human_review_required`;
- `human_authorization_reference`;
- `worker_evidence_references`;
- `worker_evidence_hash`;
- `fail_closed`;
- `failure_reason`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;
- `live_trading_performed`;
- `financial_claim_made`;
- `strategy_implemented`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Allowed Validation Results

Allowed values:

- `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- `REJECTED_BY_GOVERNANCE`;
- `FAILED_CLOSED`;
- `INSUFFICIENT_EVIDENCE`;
- `UNACCEPTABLE_RISK`;
- `OUT_OF_SCOPE`;
- `SIMULATION_ONLY`.

## Required False Flags

For all foundation-stage artifacts:

```text
broker_invoked = false
exchange_invoked = false
order_placed = false
live_trading_performed = false
financial_claim_made = false
strategy_implemented = false
strategy_deployed = false
portfolio_mutated = false
```

## Hash Requirements

Every artifact must be hashable and replay-visible.

Any nested evidence body must have a corresponding hash field.

Hash mismatch requires:

```text
FAILED_CLOSED
```

## Non-Goals

This artifact model does not implement:

- serializers;
- runtime validators;
- worker code;
- broker adapters;
- exchange adapters;
- order schemas;
- live trading state.
