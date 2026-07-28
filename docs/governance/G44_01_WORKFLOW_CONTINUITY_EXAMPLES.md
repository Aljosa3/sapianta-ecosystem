# G44-01 Workflow Continuity Examples

## Compliant repair

G43 diagnoses `G42_WORKFLOW_INPUT_BINDING` at rank 1. G44 checkpoints the
workflow and preserves rank 0, `PLATFORM_CHANGE_NORMALIZATION`. The external
repair changes only rank 1 and supplies passing evidence for the exact G43
re-validation scope. Post-repair G42 and G43 evidence proves ranks 1 through 9.
G44 declares the existing workflow eligible to continue from rank 1; rank 0
is not repeated.

## Repair outside the boundary

The same checkpoint reports rank 1, but external evidence claims a change to
`IVE_0_IMPACT_ANALYSIS`. G44 returns `RESUME_FAILED_CLOSED`; it does not widen
the repair boundary.

## Stale checkpoint

An external mutation supersedes the checkpoint and an additive invalidation
record binds that fact to the checkpoint hash. Any later resume attempt with
that checkpoint returns `RESUME_FAILED_CLOSED`.

## Replay or lineage mismatch

If a replay wrapper changes, replay reconstruction fails. If a preserved
stage has a different post-repair artifact hash, lineage verification fails.
Neither case grants continuation eligibility.

## Missing or skipped evidence

If validation evidence is absent, not passing, or bound to another scope, G44
fails closed. If any boundary at or after the resume rank lacks post-repair
evidence, G44 treats the workflow as skipped and fails closed.

