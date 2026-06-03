# TRADING_MARKET_EVIDENCE_NORMALIZATION_REPLAY_MODEL_V1

## Status

Trading Market Evidence Normalization replay model.

## Replay Purpose

Replay must allow an operator to reconstruct:

- which market evidence was normalized;
- which chain the evidence belonged to;
- which input hashes were validated;
- which fields were normalized;
- which diagnostics were produced;
- whether the result was valid, insufficient, stale, malformed, ambiguous, or failed closed;
- whether forbidden authority was absent.

## Required Replay Steps

Minimum replay steps:

```text
market_evidence_normalization_started
market_evidence_input_validated
market_evidence_normalized
market_evidence_integrity_recorded
market_evidence_normalization_returned
```

## Required Replay Fields

Every replay-visible normalization bundle must include:

- `worker_evidence_id`;
- `canonical_chain_id`;
- `input_market_evidence_reference`;
- `input_market_evidence_hash`;
- `normalized_market_evidence_reference`;
- `normalized_market_evidence_hash`;
- `source_id`;
- `instrument_id`;
- `observed_at`;
- `normalized_at`;
- `freshness_status`;
- `evidence_integrity_status`;
- `normalization_diagnostics_hash`;
- `replay_reference`;
- `replay_visible`;
- `broker_invoked`;
- `exchange_invoked`;
- `order_placed`;
- `live_trading_performed`;
- `portfolio_mutated`;
- `strategy_deployed`.

## Hash Requirements

Replay must validate:

- wrapper hash;
- input market evidence hash;
- normalized market evidence hash;
- diagnostics hash;
- returned-event hash.

Any mismatch requires:

```text
FAILED_CLOSED_REPLAY_INTEGRITY
```

## Continuity Requirements

Continuity requires:

- canonical chain id present on every normalization artifact;
- input evidence chain id matches normalized evidence chain id;
- replay references are present;
- required hashes match;
- normalization output references the exact validated input evidence.

Continuity failure requires:

```text
FAILED_CLOSED_REPLAY_INTEGRITY
```

## Forbidden Replay States

Replay must fail closed if any normalization artifact records:

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

- `VALID_NORMALIZED_MARKET_EVIDENCE`;
- `INSUFFICIENT_MARKET_EVIDENCE`;
- `MALFORMED_PRICE_EVIDENCE`;
- `MALFORMED_VOLUME_EVIDENCE`;
- `AMBIGUOUS_INSTRUMENT_EVIDENCE`;
- `STALE_MARKET_EVIDENCE`;
- `FAILED_CLOSED_REPLAY_INTEGRITY`;
- `FAILED_CLOSED_AUTHORITY_BOUNDARY`.

## Non-Goals

This replay model does not implement:

- runtime code;
- live data replay;
- broker event replay;
- exchange event replay;
- order audit;
- portfolio ledger replay.

