# G44-01 Continuity Replay Examples

## Checkpoint replay

```text
000_g42_workflow_bound.json
001_g43_supervisor_diagnosis_bound.json
002_constitutional_development_checkpoint_recorded.json
003_constitutional_development_resume_point_recorded.json
```

Reconstruction verifies wrapper ordering and hashes, validates all four
artifacts, and rechecks that checkpoint and resume identities bind to the same
G42 workflow and G43 diagnosis.

## Continuation replay

```text
000_constitutional_development_checkpoint_bound.json
001_constitutional_development_resume_point_bound.json
002_external_repair_evidence_bound.json
003_post_repair_g42_workflow_bound.json
004_post_repair_g43_diagnosis_bound.json
005_continuation_decision_recorded.json
```

A successful final artifact contains
`CONTINUATION_AUTHORIZED_FROM_RESUME_POINT` while
`execution_authorized`, `mutation_authorized`, and
`validation_execution_authorized` remain false.

## Invalidation replay

```text
000_checkpoint_invalidation_recorded.json
```

Invalidation is additive. The original checkpoint and resume point retain
their hashes. A continuation request carrying the matching invalidation fails
closed.

## Duplicate replay

Every checkpoint, invalidation, and continuation replay directory is
single-use. If a canonical wrapper already exists, a second attempt records no
replacement and returns a fail-closed result.

