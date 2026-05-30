# Constitutional Memory Fail-Closed Requirements V1

Status: fail-closed requirements for future runtime access.

## Required Failure Conditions

Future Constitutional Memory retrieval must fail closed on:

- missing artifact
- ambiguous artifact identity
- conflicting canonical sources
- invalid lineage
- invalid certification
- invalid index entry
- invalid source classification
- derived evidence presented as canonical
- unreadable source
- malformed JSON certification artifact
- stale or superseded baseline ambiguity
- replay evidence hash mismatch
- unauthorized retrieval trigger
- provider-triggered retrieval attempt
- worker-triggered retrieval attempt
- memory result used as authority

## Failure Output

Failure must produce:

- deterministic failure status
- replay-visible consultation failure artifact
- source path or source identifier where safe
- no inferred answer
- no automatic repair
- no retry loop
- no execution request

## Conflict Handling

Conflicts must not be resolved by model inference.

Required behavior:

```text
CONFLICT_DETECTED
-> FAIL_CLOSED
-> RETURN CITED CONFLICT SUMMARY
-> REQUIRE GOVERNANCE REVIEW
```

## Missing Evidence Handling

Missing evidence must produce:

```text
EVIDENCE_MISSING
```

not:

```text
BEST_EFFORT_CONSTITUTIONAL_ANSWER
```

