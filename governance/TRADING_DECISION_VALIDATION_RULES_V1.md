# TRADING_DECISION_VALIDATION_RULES_V1

## Status

Review-only validation rules.

## Rule Classes

Trading Decision Validation criteria are classified as:

- mandatory rules;
- advisory rules;
- fail-closed rules.

## Mandatory Rules

### Rule M1: Decision Request Present

A Trading Decision Request must be present and replay-visible.

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M2: Canonical Chain Present

All artifacts must include the same `canonical_chain_id`.

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M3: Market Evidence Present

Market Evidence must be present, source-identified, timestamped, and freshness-classified.

Failure outcome:

```text
INSUFFICIENT_EVIDENCE
```

### Rule M4: Portfolio Context Present Where Required

Portfolio Context must be present when the decision affects exposure, allocation, or position context.

Failure outcome:

```text
INSUFFICIENT_EVIDENCE
```

### Rule M5: Risk Context Present

Risk Context must be present and include risk result and reason hash.

Failure outcome:

```text
INSUFFICIENT_EVIDENCE
```

### Rule M6: Policy Constraints Present

Policy Constraint Context must be present.

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M7: Evidence Hashes Present

All required references must have matching hashes.

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M8: Replay Visibility Present

All validation artifacts must be replay-visible.

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M9: No Live Execution

The following must remain false:

```text
broker_invoked
exchange_invoked
order_placed
live_trading_performed
portfolio_mutated
strategy_deployed
financial_claim_made
```

Failure outcome:

```text
FAILED_CLOSED
```

### Rule M10: Human Review Requirement Present

The validation result must state whether human review is required.

Failure outcome:

```text
FAILED_CLOSED
```

## Advisory Rules

### Rule A1: Explanation Quality

Recommendation should include a clear human-readable reason.

Failure outcome:

```text
ADVISORY_WARNING
```

### Rule A2: Scenario Breadth

Recommendation should identify which scenario contexts were considered.

Failure outcome:

```text
ADVISORY_WARNING
```

### Rule A3: Source Diversity

Market Evidence should disclose whether one or multiple data sources were used.

Failure outcome:

```text
ADVISORY_WARNING
```

### Rule A4: Alternative Comparison

Recommendation may identify rejected alternatives when available.

Failure outcome:

```text
ADVISORY_WARNING
```

### Rule A5: Learning Feedback

Validation result may attach learning feedback for evidence, policy, or explanation improvement.

Failure outcome:

```text
ADVISORY_WARNING
```

## Fail-Closed Rules

Validation must fail closed if:

- replay hash mismatch occurs;
- artifact hash mismatch occurs;
- canonical chain continuity fails;
- broker invocation is detected;
- exchange invocation is detected;
- order placement is detected;
- live trading is detected;
- portfolio mutation is detected;
- financial claim is detected;
- policy context is absent;
- human authorization is ambiguous.

## Rule Precedence

Mandatory and fail-closed rules override advisory rules.

Advisory warnings cannot convert an invalid recommendation into an admissible recommendation.

Advisory warnings cannot create execution authority.
