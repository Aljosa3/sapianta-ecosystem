# AIGOL_REAL_OUTPUT_BINDING_REUSE_PLAN_V1

## Status

Review-only reuse plan.

## Principle

`FIRST_REAL_ARTIFACT_CREATION_V1` should reuse the existing execution stack. It
should add a narrow output commit boundary, not a new execution system.

## Minimum Safe Architecture

```text
WORKER_RESULT_VALIDATION_ARTIFACT_V1
-> EXACT_OUTPUT_MUTATION_AUTHORIZATION_ARTIFACT_V1
-> REAL_OUTPUT_BINDING_RUNTIME_V1
-> REAL_ARTIFACT_CREATION_ARTIFACT_V1
-> POST_EXECUTION_REPLAY_REVIEW_ARTIFACT_V1
-> GOVERNED_TERMINATION_ARTIFACT_V1
```

## Reuse Unchanged

- Use implementation handoff planned artifacts as the source of exact output
  paths.
- Use current execution lineage and hash references as required inputs.
- Use canonical serialization, replay hashing, and immutable JSON replay
  writes.
- Use workspace containment validation and execution gate validation.
- Use the create-only filesystem Worker behavior for the first artifact.

## Reuse With Binding

- Bind `allowed_outputs` and `produced_outputs` to a canonical output manifest.
- Bind a new mutation authorization to the validated result, manifest hash,
  exact paths, artifact types, content hashes, workspace root, and create-only
  mode.
- Bind filesystem Worker creation evidence into post-execution replay review.
- Bind reviewed creation continuity into governed termination.

## Do Not Reuse As Authority

- Provider proposals are not mutation authority.
- Implementation handoff approval is not mutation authority.
- Current execution authorization is not mutation authority.
- Worker dispatch, invocation, result capture, and result validation are not
  mutation authority.
- Bounded Codex execution is not mutation authority.
- Termination is not mutation authority.

## Phase 1: One Create-Only Governance Artifact

Scope:

- one new Markdown or JSON governance artifact;
- one exact repository-relative path;
- one canonical artifact type;
- content embedded or referenced immutably;
- create-only operation;
- no overwrite, append, delete, rename, or automatic retry.

Acceptance:

- missing or invalid mutation authorization fails closed;
- path escape or existing target fails closed;
- created content hash matches the manifest;
- creation evidence is replay-visible;
- replay review verifies creation continuity;
- lifecycle terminates only after successful review.

## Phase 2: Multi-Artifact Domain Bundle

Scope:

- governance artifact;
- model or domain artifact;
- certification artifact;
- explicit all-or-fail or staged commit semantics;
- one manifest entry and creation evidence entry per output.

Acceptance:

- no silent partial domain creation;
- exact output set verification;
- deterministic failure evidence;
- replay reconstruction covers every artifact.

## Phase 3: Optional Generated Implementation Content

Use bounded Codex execution only when artifact content cannot be produced
deterministically. Keep provider output non-authoritative and require the same
output manifest, mutation authorization, validation, and replay review before
any file is written.

## Recommended Next Milestone

`FIRST_REAL_ARTIFACT_CREATION_V1`

Implementation vehicle:

`AIGOL_REAL_OUTPUT_BINDING_RUNTIME_V1`

The first proof should create one new governance artifact. A successful proof
can then be extended to the multi-file artifacts required by:

```text
Create a marketing domain.
-> Real governance artifacts appear on disk.
-> Replay records creation.
-> Lifecycle terminates.
```

