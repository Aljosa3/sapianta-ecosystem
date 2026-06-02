# TRADING_POLICY_REJECTION_RULES_V1

## Status

Review-only policy rejection rules.

## Purpose

Define policy conditions that require rejection of a Trading Decision Validation recommendation.

Rejection is a governance outcome and does not create trading action.

## Automatic Rejection Rules

### R1: Insufficient Evidence

Reject when mandatory evidence is missing, stale, unhashable, not replay-visible, not chain-linked, or internally inconsistent.

Outcome:

```text
INSUFFICIENT_EVIDENCE
```

### R2: Incomplete Portfolio Context

Reject when portfolio-aware validation is required and portfolio context is incomplete.

Outcome:

```text
INCOMPLETE_PORTFOLIO_CONTEXT
```

### R3: Unacceptable Risk

Reject when risk context reports prohibited risk or cannot bound risk sufficiently for human review.

Outcome:

```text
UNACCEPTABLE_RISK
```

### R4: Policy Violation

Reject when the request, evidence, recommendation, or worker report violates active policy constraints.

Outcome:

```text
POLICY_VIOLATION
```

### R5: Out Of Scope

Reject when the request asks for live trading, broker invocation, exchange invocation, order placement, financial advice, or strategy deployment.

Outcome:

```text
OUT_OF_SCOPE
```

### R6: Financial Claim

Reject when the recommendation makes a profitability, suitability, risk-free, compliance guarantee, or market prediction certainty claim.

Outcome:

```text
POLICY_VIOLATION
```

### R7: Strategy Deployment Request

Reject when the request asks to implement, deploy, optimize, or activate a trading strategy.

Outcome:

```text
OUT_OF_SCOPE
```

## Fail-Closed Rejection Rules

Fail closed when:

- replay hash mismatch occurs;
- artifact hash mismatch occurs;
- chain continuity fails;
- replay visibility is missing;
- broker invocation is detected;
- exchange invocation is detected;
- order placement is detected;
- live trading is detected;
- portfolio mutation is detected;
- human authorization is ambiguous.

Outcome:

```text
FAILED_CLOSED
```

## Rejection Evidence Requirements

Each rejection must record:

- rejection rule id;
- rejection category;
- rejection reason;
- rejection reason hash;
- evidence references;
- canonical chain id;
- replay reference;
- no-live-execution flags.

## Rejection Boundary

Rejection does not:

- close positions;
- place opposite orders;
- mutate portfolio state;
- alter policy;
- trigger worker execution;
- prove trading performance.
