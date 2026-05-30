# Constitutional Memory Fail-Closed Retrieval V1

Status: fail-closed retrieval rules.

## Fail-Closed Conditions

Retrieval must fail closed on:

- missing artifact
- ambiguous artifact
- conflicting artifact
- invalid artifact
- invalid lineage
- invalid certification
- invalid index reference
- invalid source classification
- missing citation
- non-replay-visible retrieval
- unauthorized retrieval trigger
- provider-triggered retrieval
- worker-triggered retrieval
- derived source presented as canonical
- retrieval output used as authority

## Failure Artifacts

Failure output must include:

- deterministic failure status
- failed source identifier where safe
- failure reason
- requesting entity classification
- replay-visible failure record
- no inferred constitutional answer
- no automatic repair
- no retry loop
- no execution request
- no authorization result

## Conflict Rule

Conflicts must produce:

```text
CONFLICT_DETECTED
```

and require governance review.

Retrieval must not infer which constitutional source wins unless the answer is directly determined by the canonical source hierarchy.

## Missing Evidence Rule

Missing evidence must produce:

```text
EVIDENCE_MISSING
```

not an approximation.

