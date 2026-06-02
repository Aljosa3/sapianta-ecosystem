# TRADING_POLICY_CONSTRAINT_MODEL_V1

## Status

Review-only policy constraint model.

## Constraint Classes

Trading Decision Validation policy constraints are grouped as:

- evidence constraints;
- replay constraints;
- risk constraints;
- portfolio constraints;
- strategy constraints;
- authority constraints;
- human review constraints;
- advisory quality constraints.

## Evidence Constraints

Mandatory:

- decision request present;
- market evidence present;
- risk context present;
- strategy context present;
- policy context present;
- portfolio context present where required;
- all mandatory evidence hash-linked;
- all mandatory evidence replay-visible.

Advisory:

- additional data source comparison;
- scenario comparison;
- rejected alternative comparison;
- explanation evidence.

## Replay Constraints

Mandatory:

- canonical chain id present;
- replay reference present;
- artifact hashes present;
- wrapper hashes present where replay wrappers exist;
- validation reason hash present;
- no-live-execution flags present;
- fail-closed reasons replay-visible.

Advisory:

- audit-friendly grouping;
- operator-readable summaries;
- cross-reference to dashboard or chain inspection commands.

## Risk Constraints

Mandatory:

- risk context present;
- risk policy reference present;
- risk result present;
- risk reason hash present;
- prohibited risk states rejected.

Advisory:

- additional scenario analysis;
- sensitivity notes;
- confidence narration;
- learning feedback for ambiguous risk criteria.

## Portfolio Constraints

Mandatory when portfolio-aware validation is required:

- portfolio scope present;
- position context hash present;
- exposure context hash present;
- hypothetical-only marker present;
- portfolio mutation false flag present.

Advisory:

- allocation context summary;
- concentration narrative;
- alternative exposure comparison.

## Strategy Constraints

Mandatory:

- strategy context present;
- strategy claim summary present;
- strategy implementation false flag present;
- strategy deployment false flag present.

Advisory:

- scenario or historical context;
- alternative strategy comparison;
- explanation of unsupported assumptions.

## Authority Constraints

Mandatory:

- broker invocation false;
- exchange invocation false;
- order placement false;
- live trading false;
- portfolio mutation false;
- financial claim false;
- human review requirement present.

These constraints cannot be advisory.

## Human Review Constraints

Mandatory:

- human review required for admissible recommendations;
- human review required for material risk;
- human review required for policy ambiguity;
- human review required for learning proposals that affect policy, evidence, or thresholds.

## Advisory Quality Constraints

Advisory:

- explanation clarity;
- operator readability;
- audit package clarity;
- scenario breadth;
- market source diversity;
- learning suggestion quality.

Advisory constraints may produce warnings only.

They cannot create admissibility when mandatory constraints fail.

## Constraint Precedence

Precedence order:

```text
fail-closed constraints
mandatory authority constraints
mandatory replay constraints
mandatory evidence constraints
mandatory risk and portfolio constraints
human review constraints
advisory quality constraints
```
