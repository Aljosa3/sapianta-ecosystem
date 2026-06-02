# TRADING_POLICY_ESCALATION_RULES_V1

## Status

Review-only policy escalation rules.

## Purpose

Define policy conditions that require escalation to human review.

Escalation is review-only and does not authorize trading.

## Escalation Rules

### E1: Admissible For Human Review

Escalate when validation result is:

```text
ADMISSIBLE_FOR_HUMAN_REVIEW
```

Meaning:

Evidence is sufficient for human review, not execution.

### E2: Material Risk

Escalate when evidence is complete but risk remains material, complex, or policy-sensitive.

Examples:

- exposure impact;
- concentration impact;
- liquidity sensitivity;
- volatility sensitivity;
- drawdown sensitivity.

### E3: Policy Ambiguity

Escalate when policy interpretation is unclear.

Examples:

- asset class classification unclear;
- instrument status unclear;
- venue status unclear;
- evidence freshness policy ambiguous;
- risk threshold needs interpretation.

### E4: Portfolio Exposure Impact

Escalate when the decision affects or simulates exposure, allocation, concentration, or position context.

### E5: Learning Policy Proposal

Escalate when governed learning proposes:

- policy refinement;
- evidence requirement change;
- risk threshold review;
- replay model refinement;
- worker quality change.

### E6: Fail-Closed Audit

Escalate for operator audit when validation fails closed due to integrity, replay, authority, or chain continuity concerns.

Audit escalation must not repair replay through this model.

## Escalation Evidence Requirements

Each escalation must record:

- escalation rule id;
- escalation category;
- source validation result;
- escalation reason;
- escalation reason hash;
- evidence references;
- canonical chain id;
- replay reference;
- human review required flag;
- no-live-execution flags.

## Escalation Boundary

Escalation does not:

- approve a recommendation;
- authorize a broker;
- authorize an exchange;
- create an order;
- create a live execution request;
- mutate portfolio state;
- change risk limits;
- change policy.

## Escalation Precedence

Fail-closed and rejection rules occur before escalation.

Escalation is appropriate when evidence is reviewable or audit-worthy, not when it can be converted into action.
