# Intent Classifier Replay Model V1

Status: replay model for Intent Classifier.

## Replay Visibility Classification

`INTENT_CLASSIFIER_REPLAY_VISIBILITY`: `MANDATORY`

## Replay Requirement

Every classification attempt must be replay-visible.

Replay must include:

- classifier input reference
- normalized request reference when present
- optional cited memory context references
- candidate destination
- classification status
- ambiguity status
- failure reason when failed
- artifact hash
- lineage to routing artifact

## Replay Sequence

Future sequence:

```text
Human Prompt Evidence
-> Intent Classification Artifact
-> Intent Routing Artifact
-> Destination Boundary
```

## Replay Failure

If classification replay is missing, corrupted, ambiguous, or unordered, downstream routing must fail closed.

## Replay Boundary

Replay is evidence.

Replay does not authorize, govern, execute, or select the destination by itself.

