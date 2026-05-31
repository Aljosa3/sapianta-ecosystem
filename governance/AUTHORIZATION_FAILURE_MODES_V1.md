# AUTHORIZATION_FAILURE_MODES_V1

## Status

Certified authorization failure modes.

## Fail-Closed Principle

Unresolved authorization states fail closed.

Ambiguity is not permission.

Missing evidence is not permission.

Replay gaps are not permission.

## Failure Modes

| Failure Mode | Required Outcome |
| --- | --- |
| missing authorization | FAIL_CLOSED |
| missing evidence | FAIL_CLOSED |
| unknown worker | FAIL_CLOSED |
| worker mismatch | FAIL_CLOSED |
| scope mismatch | FAIL_CLOSED |
| expired authorization | FAIL_CLOSED |
| malformed authorization | FAIL_CLOSED |
| missing proposal lineage | FAIL_CLOSED |
| missing governance review | FAIL_CLOSED |
| missing replay reference | FAIL_CLOSED |
| authority escalation attempt | FAIL_CLOSED |
| worker self-authorization attempt | FAIL_CLOSED |

## Rejection vs Failure

`REJECTED` applies when the request is understood and constitutionally
inadmissible.

`FAILED` applies when the authorization disposition cannot be trusted due to
ambiguity, corruption, missing evidence, invalid lineage, or bypass pressure.

## Certification

No worker execution may proceed from a failed authorization state.
