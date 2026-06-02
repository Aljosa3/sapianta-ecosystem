# TRADING_DECISION_FIXTURE_REPLAY_MODEL_V1

## Status

Review-only fixture replay model.

## Replay Purpose

Fixture replay must make future Trading Worker tests reconstructable before workers exist.

Each fixture should show:

- input evidence;
- expected validation outcome;
- expected rejection or escalation category;
- no-live-execution boundary;
- fail-closed trigger where applicable.

## Required Fixture Replay Steps

Recommended replay steps:

```text
fixture_declared
decision_request_recorded
market_evidence_recorded
portfolio_context_recorded
risk_context_recorded
strategy_context_recorded
policy_constraints_recorded
expected_validation_recorded
fixture_replay_returned
```

If a fixture is not portfolio-aware, `portfolio_context_recorded` may be marked:

```text
NOT_REQUIRED
```

## Required Replay Fields

Every fixture replay bundle should include:

- `fixture_id`;
- `fixture_category`;
- `canonical_chain_id`;
- `trading_decision_id`;
- `decision_request_reference`;
- `decision_request_hash`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `portfolio_context_reference`;
- `portfolio_context_hash`;
- `risk_context_reference`;
- `risk_context_hash`;
- `strategy_context_reference`;
- `strategy_context_hash`;
- `policy_constraint_reference`;
- `policy_constraint_hash`;
- `expected_validation_result`;
- `expected_rejection_category`;
- `expected_escalation_category`;
- `expected_fail_closed`;
- `replay_reference`;
- `replay_visible`;
- `fixture_hash`.

## Replay Integrity Requirements

Future fixture implementations should validate:

- wrapper hash;
- fixture hash;
- artifact hash;
- evidence hash continuity;
- canonical chain continuity;
- expected outcome consistency;
- no-live-execution flags.

## Fail-Closed Fixture Replay

Fail-closed fixtures must record the intentional corruption or authority violation as fixture setup.

Examples:

- replay hash mismatch;
- artifact hash mismatch;
- chain continuity failure;
- broker invocation true;
- exchange invocation true;
- order placed true;
- portfolio mutated true;
- strategy deployed true;
- financial claim true.

The fixture expected outcome must be:

```text
FAILED_CLOSED
```

## Replay Organization

Recommended future layout:

```text
governance/trading/fixtures/
  valid/
  insufficient_evidence/
  portfolio_context/
  risk/
  policy_violation/
  escalation/
  learning/
  fail_closed/
  advisory/
```

Each fixture directory should contain:

- fixture declaration;
- evidence artifacts;
- expected validation artifact;
- replay manifest;
- certification reference.

## Boundary

Fixture replay does not execute workers.

Fixture replay does not call providers, brokers, exchanges, or market data APIs.

Fixture replay does not place orders.
