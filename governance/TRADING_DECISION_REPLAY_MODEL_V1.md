# TRADING_DECISION_REPLAY_MODEL_V1

## Status

Review-only replay model.

## Replay Purpose

Trading Decision Replay must allow a human operator to reconstruct:

- what decision was proposed;
- what evidence accompanied it;
- what workers participated;
- what risk and policy checks occurred;
- what validation result was produced;
- why the result was admissible, rejected, insufficient, or failed closed;
- whether any forbidden execution behavior occurred.

## Required Replay Chain

Minimum replay chain:

```text
trading_decision_requested
market_evidence_recorded
portfolio_context_recorded
strategy_context_recorded
risk_context_recorded
policy_constraints_recorded
trading_decision_validated
trading_learning_feedback_recorded
```

## Required Replay Fields

Each replay-visible decision validation bundle must include:

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
- `validation_result_reference`;
- `validation_result_hash`;
- `worker_evidence_references`;
- `worker_evidence_hash`;
- `learning_feedback_reference`;
- `learning_feedback_hash`;
- `replay_reference`;
- `replay_visible`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;
- `live_trading_performed`.

## Hash Requirements

Replay must validate:

- wrapper hashes;
- artifact hashes;
- nested evidence hashes;
- worker evidence hashes;
- validation reason hashes;
- learning feedback hashes.

Any mismatch fails closed.

## Continuity Requirements

All decision validation artifacts must share a canonical chain id.

Continuity failure occurs when:

- artifact chain ids differ;
- required artifact references are missing;
- referenced hashes do not match;
- replay ordering is invalid;
- validation result refers to evidence outside the chain without an explicit governed reference.

Continuity failure requires:

```text
FAILED_CLOSED
```

## Forbidden Replay States

Replay must fail closed if any foundation-stage artifact records:

```text
broker_invoked = true
exchange_invoked = true
order_placed = true
live_trading_performed = true
portfolio_mutated = true
strategy_deployed = true
financial_claim_made = true
```

## Replay Outcomes

Allowed reconstructed outcomes:

- `ADMISSIBLE_FOR_HUMAN_REVIEW`;
- `REJECTED_BY_GOVERNANCE`;
- `FAILED_CLOSED`;
- `INSUFFICIENT_EVIDENCE`;
- `UNACCEPTABLE_RISK`;
- `OUT_OF_SCOPE`;
- `SIMULATION_ONLY`.

## Learning Attachment Replay

Learning feedback must be recorded as advisory, governed evidence.

Replay must show:

- source validation result;
- feedback type;
- proposed improvement, if any;
- human approval requirement;
- implementation authority absent;
- execution authority absent.

Learning feedback must not mutate the original decision replay.

## Non-Goals

This replay model does not implement:

- replay runtime code;
- broker event replay;
- exchange event replay;
- live order audit;
- portfolio ledger mutation;
- financial performance reporting.
