# TRADING_MARKET_EVIDENCE_NORMALIZATION_FIXTURE_COVERAGE_V1

## Status

Trading Market Evidence Normalization fixture coverage.

## Fixture Purpose

Fixtures define canonical evidence scenarios for future runtime and worker testing.

They do not implement a worker.

## Fixture Categories

### Valid Minimal Market Evidence

Fixture:

```text
TMEN_FIXTURE_VALID_MINIMAL_MARKET_EVIDENCE
```

Expected:

```text
VALID_NORMALIZED_MARKET_EVIDENCE
```

Purpose:

Confirm that complete market evidence normalizes deterministically.

### Insufficient Market Evidence

Fixture:

```text
TMEN_FIXTURE_INSUFFICIENT_MARKET_EVIDENCE
```

Expected:

```text
INSUFFICIENT_MARKET_EVIDENCE
```

Purpose:

Confirm that missing mandatory evidence is rejected.

### Malformed Price Evidence

Fixture:

```text
TMEN_FIXTURE_MALFORMED_PRICE_EVIDENCE
```

Expected:

```text
MALFORMED_PRICE_EVIDENCE
```

Purpose:

Confirm that invalid price evidence does not normalize silently.

### Malformed Volume Evidence

Fixture:

```text
TMEN_FIXTURE_MALFORMED_VOLUME_EVIDENCE
```

Expected:

```text
MALFORMED_VOLUME_EVIDENCE
```

Purpose:

Confirm that invalid volume evidence does not normalize silently.

### Ambiguous Instrument Evidence

Fixture:

```text
TMEN_FIXTURE_AMBIGUOUS_INSTRUMENT_EVIDENCE
```

Expected:

```text
AMBIGUOUS_INSTRUMENT_EVIDENCE
```

Purpose:

Confirm that ambiguous instrument identity fails closed or rejects normalization.

### Stale Market Evidence

Fixture:

```text
TMEN_FIXTURE_STALE_MARKET_EVIDENCE
```

Expected:

```text
STALE_MARKET_EVIDENCE
```

Purpose:

Confirm that stale evidence is surfaced as diagnostics and cannot be treated as fresh.

### Replay Hash Mismatch

Fixture:

```text
TMEN_FIXTURE_REPLAY_HASH_MISMATCH
```

Expected:

```text
FAILED_CLOSED_REPLAY_INTEGRITY
```

Purpose:

Confirm that replay corruption fails closed.

### Authority Boundary Violation

Fixture:

```text
TMEN_FIXTURE_AUTHORITY_BOUNDARY_VIOLATION
```

Expected:

```text
FAILED_CLOSED_AUTHORITY_BOUNDARY
```

Purpose:

Confirm that broker, exchange, order, portfolio, or strategy authority markers fail closed.

## Mandatory Fixture Fields

Every fixture must include:

- `fixture_id`;
- `fixture_version`;
- `fixture_category`;
- `canonical_chain_id`;
- `market_evidence_reference`;
- `market_evidence_hash`;
- `source_id`;
- `instrument_id`;
- `observed_at`;
- `price_evidence`;
- `volume_evidence`;
- `metadata_evidence`;
- `expected_integrity_status`;
- `expected_fail_closed`;
- `replay_reference`;
- `replay_visible`.

## Required False Flags

Every fixture must record:

```text
broker_invoked = false
exchange_invoked = false
order_placed = false
live_trading_performed = false
portfolio_mutated = false
strategy_deployed = false
```

Authority violation fixtures may set exactly one forbidden marker to true to verify fail-closed detection.

## Coverage Judgment

Fixture coverage is sufficient for worker foundation certification.

Runtime implementation should convert these fixture categories into executable tests.

