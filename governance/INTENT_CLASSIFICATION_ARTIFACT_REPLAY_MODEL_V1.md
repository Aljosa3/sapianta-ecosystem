# Intent Classification Artifact Replay Model V1

Status: replay model for the Intent Classification Artifact.

## Replay Classification

`INTENT_CLASSIFICATION_ARTIFACT_REPLAY`: `MANDATORY`

## Mandatory Replay Contents

Replay must include:

- artifact identity
- human request reference
- human prompt hash
- classification destination
- classification reason
- classification timestamp
- classification version
- replay linkage
- reconstruction metadata
- ambiguity status
- artifact hash

## Optional Replay Contents

Replay may include:

- normalized request reference
- cited Constitutional Memory references
- confidence semantics

## Forbidden Replay Contents

Replay must not contain hidden context or authority-bearing outputs.

## Replay Sequence

Canonical sequence:

```text
Human Prompt Evidence
-> Intent Classification Artifact
-> Intent Routing Artifact
-> Destination Boundary
```

## Replay Failure

Missing, corrupt, ambiguous, unordered, or non-reconstructable classification replay must fail closed.

