# TRADING_DOMAIN_MODEL_V1

## Status

Foundation-only trading domain model.

## Domain Identity

```text
domain_id = TRADING
domain_name = Trading Domain
domain_class = AI_DECISION_VALIDATION_DOMAIN
```

## Domain Purpose

The Trading Domain validates proposed trading-related decisions under governed evidence, replay visibility, risk constraints, and human authorization boundaries.

It does not execute trades.

## Core Domain Objects

### Trading Decision Request

A proposed trading-related decision requiring validation.

Examples:

- evaluate whether a proposed position change is admissible;
- evaluate whether a strategy signal is sufficiently evidenced;
- evaluate whether a portfolio adjustment violates constraints;
- evaluate whether a trading recommendation should be rejected.

### Market Evidence

Replay-visible evidence describing relevant market context.

Examples:

- prices;
- volumes;
- spread context;
- volatility context;
- timestamped market snapshots;
- data source identity;
- data freshness.

### Strategy Evaluation

Replay-visible evaluation of a strategy claim or proposed action.

This is evidence, not execution authority.

### Risk Analysis

Replay-visible assessment of risk constraints.

Examples:

- exposure limits;
- concentration limits;
- liquidity constraints;
- volatility constraints;
- drawdown constraints;
- counterparty or venue constraints where applicable.

### Portfolio Context

Replay-visible context about current or hypothetical portfolio state.

This foundation does not authorize real portfolio mutation.

### Trading Validation Result

Governed output of the domain validation process.

Allowed result classes:

- `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- `REJECTED_BY_GOVERNANCE`;
- `FAILED_CLOSED`;
- `INSUFFICIENT_EVIDENCE`;
- `OUT_OF_SCOPE`;
- `SIMULATION_ONLY`.

No result class means order placement.

## Minimal Lifecycle

```text
TRADING_DECISION_REQUESTED
MARKET_EVIDENCE_ATTACHED
PORTFOLIO_CONTEXT_ATTACHED
STRATEGY_EVALUATED
RISK_ANALYZED
GOVERNANCE_VALIDATED
HUMAN_REVIEW_REQUIRED
TRADING_DECISION_RECORDED
LEARNING_FEEDBACK_AVAILABLE
```

## Required Evidence Fields

Minimum replay-visible fields:

- `trading_decision_id`;
- `canonical_chain_id`;
- `decision_request_reference`;
- `decision_request_hash`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `strategy_evaluation_reference`;
- `strategy_evaluation_hash`;
- `risk_analysis_reference`;
- `risk_analysis_hash`;
- `portfolio_context_reference`;
- `portfolio_context_hash`;
- `policy_constraint_reference`;
- `policy_constraint_hash`;
- `human_review_reference`;
- `validation_result`;
- `validation_reason_hash`;
- `replay_reference`;
- `replay_visible`;
- `live_trading_performed`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;

## Domain Policy Requirements

Trading Domain policy must specify:

- admissible asset classes for validation;
- prohibited asset classes;
- minimum evidence freshness;
- minimum risk analysis requirements;
- human review requirements;
- simulation-only boundaries;
- out-of-scope conditions;
- fail-closed conditions;
- replay retention expectations.

## Fail-Closed Conditions

Trading validation must fail closed when:

- market evidence is missing;
- evidence hashes mismatch;
- market data is stale beyond policy;
- portfolio context is missing where required;
- risk analysis is missing;
- policy constraints are missing;
- human authorization is ambiguous;
- broker or exchange invocation is detected;
- order placement is attempted;
- replay visibility is missing;
- canonical chain continuity is broken.

## Non-Goals

The Trading Domain model does not define:

- trading strategies;
- trading signals;
- alpha generation;
- profitability assessment;
- broker APIs;
- exchange APIs;
- live order execution;
- capital allocation;
- financial advice.

## Relationship To Learning

Governed learning may improve:

- evidence requirements;
- validation clarity;
- risk review prompts;
- replay completeness;
- worker quality checks.

Governed learning may not:

- deploy strategies;
- change risk constraints autonomously;
- approve trades;
- place orders;
- mutate portfolio state.
