# TRADING_DECISION_FIXTURE_COVERAGE_V1

## Status

Review-only fixture coverage model.

## Coverage Objective

The fixture set must cover all certified Trading Decision Validation acceptance and policy outcomes before Trading Workers are implemented.

## Coverage Matrix

| Fixture | Category | Expected Outcome | Boundary Covered |
| --- | --- | --- | --- |
| `TDV_FIXTURE_VALID_MINIMAL_REVIEWABLE_REQUEST` | valid | `ADMISSIBLE_FOR_HUMAN_REVIEW` | baseline admissible review |
| `TDV_FIXTURE_INSUFFICIENT_MARKET_EVIDENCE` | insufficient evidence | `INSUFFICIENT_EVIDENCE` | missing mandatory evidence |
| `TDV_FIXTURE_INCOMPLETE_PORTFOLIO_CONTEXT` | portfolio context | `INCOMPLETE_PORTFOLIO_CONTEXT` | incomplete portfolio context |
| `TDV_FIXTURE_UNACCEPTABLE_RISK` | risk | `UNACCEPTABLE_RISK` | prohibited risk |
| `TDV_FIXTURE_POLICY_VIOLATION` | policy violation | `POLICY_VIOLATION` | policy rejection |
| `TDV_FIXTURE_HUMAN_REVIEW_ESCALATION` | escalation | `HUMAN_REVIEW_REQUIRED` | human review |
| `TDV_FIXTURE_LEARNING_REVIEW_ESCALATION` | learning | `LEARNING_REVIEW` | governed learning attachment |
| `TDV_FIXTURE_REPLAY_HASH_MISMATCH` | fail closed | `FAILED_CLOSED` | replay corruption |
| `TDV_FIXTURE_CHAIN_CONTINUITY_FAILURE` | fail closed | `FAILED_CLOSED` | chain continuity |
| `TDV_FIXTURE_BROKER_INVOCATION_DETECTED` | fail closed | `FAILED_CLOSED` | broker boundary |
| `TDV_FIXTURE_ORDER_PLACEMENT_DETECTED` | fail closed | `FAILED_CLOSED` | order boundary |
| `TDV_FIXTURE_ADVISORY_EXPLANATION_QUALITY` | advisory | `ADVISORY_WARNING` | optional evidence quality |

## Mandatory Coverage Categories

Mandatory fixture coverage:

- valid reviewable request;
- insufficient evidence;
- incomplete portfolio context;
- unacceptable risk;
- policy violation;
- human review escalation;
- learning review escalation;
- replay hash mismatch;
- chain continuity failure;
- broker invocation detected;
- order placement detected.

## Advisory Coverage Categories

Advisory fixture coverage:

- explanation clarity;
- scenario breadth;
- source diversity;
- alternative comparison;
- operator readability;
- audit package clarity.

## Escalation Coverage

Escalation fixture categories:

- human review required;
- material risk review;
- policy review;
- portfolio context review;
- learning review;
- fail-closed audit.

## Fail-Closed Coverage

Fail-closed fixture categories:

- replay hash mismatch;
- artifact hash mismatch;
- chain continuity failure;
- missing replay visibility;
- broker invocation detected;
- exchange invocation detected;
- order placement detected;
- live trading detected;
- portfolio mutation detected;
- strategy deployment detected;
- financial claim detected;
- human authorization ambiguity.

## Worker Readiness Coverage

The first Trading Worker should be tested against fixtures that do not require strategy, risk scoring, portfolio mutation, broker integration, exchange integration, or order placement.

Safest first worker foundation:

```text
TRADING_MARKET_EVIDENCE_NORMALIZATION_WORKER_FOUNDATION_V1
```

Reason:

It can operate read-only on explicit Market Evidence fixtures and produce normalized replay-visible evidence without strategy, risk, portfolio, broker, exchange, or order authority.

## Coverage Boundary

Fixture coverage is architecture only.

It does not implement worker code or fixture JSON files.
