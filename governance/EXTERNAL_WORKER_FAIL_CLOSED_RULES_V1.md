# External Worker Fail-Closed Rules V1

Status: fail-closed rules for the first external Worker attachment.

## Fail-Closed Conditions

The external Worker fails closed on:

- missing authorization
- invalid authorization
- invalid execution request
- identity corruption
- replay corruption
- capability mismatch
- boundary violation
- unexpected mutation attempt
- append-only replay violation

## Failure Semantics

Failure produces replay-visible terminal evidence with:

- `state = FAILED`
- `final_status = FAILED`
- deterministic failure reason
- read-only boundary preserved
- hidden continuation disabled
- worker authority absent

## No Silent Recovery

The Worker does not retry, repair, infer missing authorization, reinterpret capability targets, or continue after a failed boundary check.

## Authority Preservation

Fail-closed handling preserves:

- AiGOL governance authority
- mandatory authorization
- replay centrality
- Worker execution-only status
- read-only inspection boundary

