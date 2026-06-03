# TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_MODEL_V1

## Status

Trading Market Evidence Normalization Worker model.

## Worker Identity

```text
worker_family_id = MARKET_EVIDENCE_NORMALIZATION
domain_id = TRADING
worker_category = TRADING_SPECIFIC_EVIDENCE_WORKER
authority = EVIDENCE_TRANSFORMATION_ONLY
```

## Artifact Model

The future runtime should produce:

```text
NORMALIZED_MARKET_EVIDENCE_ARTIFACT_V1
```

Required fields:

- `artifact_type`;
- `worker_evidence_id`;
- `canonical_chain_id`;
- `input_market_evidence_reference`;
- `input_market_evidence_hash`;
- `normalized_market_evidence_id`;
- `instrument_id`;
- `instrument_symbol`;
- `source_id`;
- `source_type`;
- `observed_at`;
- `normalized_at`;
- `freshness_status`;
- `price_evidence`;
- `volume_evidence`;
- `metadata_evidence`;
- `normalization_diagnostics`;
- `evidence_integrity_status`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Input Model

Required input fields:

- `canonical_chain_id`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `source_id`;
- `instrument_id`;
- `observed_at`;
- `price_evidence`;
- `volume_evidence`;
- `metadata_evidence`;
- `replay_reference`;
- `replay_visible`.

Required authority flags:

```text
broker_invoked = false
exchange_invoked = false
order_placed = false
live_trading_performed = false
portfolio_mutated = false
strategy_deployed = false
```

## Normalization Semantics

The worker normalizes:

- instrument identifiers into canonical Trading Domain identifiers;
- timestamps into canonical observed-time fields;
- price evidence into deterministic numeric evidence fields;
- volume evidence into deterministic numeric evidence fields;
- source metadata into canonical source fields;
- freshness signals into an allowed freshness class;
- diagnostics into replay-visible evidence.

## Allowed Freshness Classes

Allowed freshness classes:

- `FRESH`;
- `STALE`;
- `UNKNOWN_FAILED_CLOSED`.

Freshness thresholds are outside this foundation and belong to future Trading policy artifacts.

## Allowed Integrity Classes

Allowed evidence integrity classes:

- `VALID_NORMALIZED_MARKET_EVIDENCE`;
- `INSUFFICIENT_MARKET_EVIDENCE`;
- `MALFORMED_PRICE_EVIDENCE`;
- `MALFORMED_VOLUME_EVIDENCE`;
- `AMBIGUOUS_INSTRUMENT_EVIDENCE`;
- `STALE_MARKET_EVIDENCE`;
- `FAILED_CLOSED_REPLAY_INTEGRITY`;
- `FAILED_CLOSED_AUTHORITY_BOUNDARY`.

## Diagnostics Model

Normalization diagnostics must include:

- missing fields;
- malformed fields;
- ambiguous fields;
- hash validation status;
- replay validation status;
- freshness assessment;
- normalization assumptions;
- fail-closed reason, if applicable.

## Non-Goals

This worker model does not implement:

- live market data collection;
- broker integration;
- exchange integration;
- order placement;
- financial advice;
- strategy evaluation;
- risk scoring;
- portfolio mutation;
- runtime worker code.

