# Intent Classifier Minimal Scope V1

Status: smallest valid implementation scope.

## Minimal Scope

The smallest safe implementation is:

```text
Human Prompt Evidence
-> Deterministic Classifier
-> Intent Classification Artifact
-> Append-Only Replay
```

## Included In V1

V1 may include:

- explicit human prompt reference
- prompt hash
- one candidate destination
- classification reason
- classification status
- ambiguity status
- classifier version
- replay parent
- lineage references
- authority guarantees
- artifact hash

## Excluded From V1

V1 must exclude:

- routing runtime
- provider invocation
- worker invocation
- memory retrieval
- execution request generation
- authorization
- correction loops
- autonomous prompt handling

## Classification Scope

`CLASSIFICATION_SCOPE`: `FULL_SCOPE_READY`

V1 may classify into all four destination labels:

- `CONVERSATION`
- `CONSTITUTIONAL_MEMORY_CONSULTATION`
- `PROVIDER_PROPOSAL`
- `EXECUTION_REQUEST`

This is safe because labels do not perform destination actions.

## Constraint

Full-scope labels are ready; full downstream routing is not part of classifier V1.

