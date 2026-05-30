# Constitutional Memory Access Fail-Closed Rules V1

Status: fail-closed rules for reference-only Constitutional Memory access.

## Fail-Closed Conditions

Constitutional Memory access fails closed on:

- missing artifact
- ambiguous artifact
- multiple canonical matches
- invalid artifact
- invalid classification
- invalid index reference
- authority-bearing request
- execution-bearing request
- forbidden requester
- missing governance context
- replay corruption
- replay ordering mismatch
- append-only replay violation

## Forbidden Requests

Requests fail closed when they ask Constitutional Memory to:

- authorize
- execute
- produce an execution request
- produce a governance decision
- produce a worker command
- produce a provider command
- generate a proposal
- issue a correction instruction
- mutate artifacts

## Failure Evidence

Failures must produce replay-visible artifacts with:

- retrieval status `FAILED_CLOSED`
- final status `FAILED`
- failure reason
- reference-only marker
- no authority-bearing output fields

## No Silent Recovery

The access path does not:

- retry
- guess
- search outside the explicit catalog
- substitute another artifact silently
- repair replay
- continue after ambiguity

## Boundary Certification

Fail-closed behavior preserves:

- citation discipline
- replay visibility
- reference-only status
- governance authority separation

