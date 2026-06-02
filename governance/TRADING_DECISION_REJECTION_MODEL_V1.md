# TRADING_DECISION_REJECTION_MODEL_V1

## Status

Review-only rejection model.

## Purpose

Define objective rejection categories for Trading Domain decision validation.

Rejection is a governance outcome, not a trading action.

## Rejection Categories

### INSUFFICIENT_EVIDENCE

Use when required evidence is missing, stale, unhashable, not replay-visible, not chain-linked, or internally inconsistent.

Examples:

- missing Market Evidence;
- missing Risk Context;
- missing Portfolio Context where required;
- stale market evidence;
- missing evidence hash;
- missing replay reference.

### INCOMPLETE_PORTFOLIO_CONTEXT

Use when portfolio-aware validation is required but portfolio context lacks scope, position hash, cash or margin hash where relevant, exposure hash, hypothetical marker, or mutation false flag.

This category may roll up into:

```text
INSUFFICIENT_EVIDENCE
```

### UNACCEPTABLE_RISK

Use when risk evidence violates policy constraints or risk cannot be bounded sufficiently for human review.

Examples:

- exposure check fails;
- concentration check fails;
- liquidity check fails;
- volatility check fails;
- drawdown check fails;
- downside scenario is ambiguous.

### POLICY_VIOLATION

Use when the request or recommendation violates policy constraints.

Examples:

- prohibited asset class;
- prohibited instrument;
- prohibited venue;
- missing human review;
- attempted live execution;
- financial performance claim;
- strategy deployment claim.

### OUT_OF_SCOPE

Use when a request is not a Trading Domain decision-validation request or asks for unavailable authority.

Examples:

- place this order;
- call this broker;
- deploy this strategy;
- provide financial advice;
- guarantee profit.

### FAILED_CLOSED

Use when replay, authority, chain continuity, or artifact integrity cannot be trusted.

Examples:

- replay hash mismatch;
- artifact hash mismatch;
- invalid reference;
- chain continuity failure;
- broker invocation detected;
- exchange invocation detected;
- order placement detected;
- human authorization ambiguity.

### REJECTED_BY_GOVERNANCE

Use as a general governed rejection result when the recommendation is inadmissible after validation.

This category may include one or more specific rejection reasons.

## Required Rejection Evidence

Every rejected recommendation should record:

- rejection category;
- rejection reason;
- rejection reason hash;
- evidence references;
- canonical chain id;
- fail-closed status;
- human review requirement;
- no-live-execution flags.

## Rejection Boundary

Rejection does not:

- place an opposing trade;
- close a position;
- mutate a portfolio;
- trigger execution;
- update policy;
- prove performance quality.

## Learning Attachment

Rejected recommendations may produce governed learning feedback.

Learning feedback may propose:

- clearer evidence requirements;
- policy clarification;
- risk review improvements;
- worker quality improvements;
- replay completeness improvements.

Learning feedback may not self-apply changes.
