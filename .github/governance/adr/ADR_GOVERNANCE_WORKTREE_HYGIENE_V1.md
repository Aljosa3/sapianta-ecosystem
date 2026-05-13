# ADR: Governance Worktree Hygiene v1

## Context

Replay-safe governance infrastructure requires deterministic artifact hygiene.

During `AGOL_LAYER_SEPARATION_MODEL_V1`, Python cache artifacts entered canonical lineage. Existing history and tags must not be rewritten, but future replay pollution must be detected and blocked deterministically.

This milestone follows:

- `STABILIZATION_CERTIFICATION_EPOCH_V1`
- `AGOL_LAYER_SEPARATION_MODEL_V1`

It does not redefine or mutate either milestone.

## Decision

Introduce `GOVERNANCE_WORKTREE_HYGIENE_V1` as a deterministic hygiene enforcement layer.

The layer classifies artifacts as:

- `CANONICAL_GOVERNANCE_ARTIFACT`
- `TRANSIENT_RUNTIME_ARTIFACT`
- `UNKNOWN_ARTIFACT`

Transient and unknown artifacts are blocked from governance lineage and require human review. The validator is read-only and performs no automatic deletion.

## Why Replay Cleanliness Matters

Governance lineage is canonical system memory. It must remain minimal, explainable, reproducible, and artifact-clean.

Cache files, compiled Python artifacts, runtime logs, and generated execution residue can pollute replay lineage because they are environment-derived rather than governance-derived.

## Why Transient Runtime Artifacts Are Dangerous

Transient artifacts can:

- encode machine-local execution residue;
- create non-minimal diffs;
- make replay evidence harder to certify;
- obscure actual governance changes;
- cause accidental canonicalization of runtime noise.

## Why Broad Cleanup Is Not Automatic

Automatic cleanup can mutate evidence unexpectedly. This milestone detects and blocks pollution but does not delete files, rewrite history, mutate tags, or alter replay references.

## Relationship To Stabilization And Layer Separation

`STABILIZATION_CERTIFICATION_EPOCH_V1` restored deterministic collection integrity. `AGOL_LAYER_SEPARATION_MODEL_V1` established authority separation. Hygiene now protects those milestones from future accidental runtime residue entering governance lineage.

## Consequences

Positive:

- Replay pollution becomes deterministic and visible.
- Cache artifacts are blocked from future governance lineage.
- Unknown artifacts fail closed.
- Worktree hygiene becomes testable.

Tradeoffs:

- Some new files require explicit classification before entering governance lineage.
- Existing polluted history remains visible rather than rewritten.

## Explicit Non-Goals

- Provider abstraction.
- Execution routing.
- Orchestration.
- Runtime optimization.
- Execution envelopes.
- Governance semantic redesign.
- Replay rewriting.
- Git history rewriting.
- Canonical tag mutation.
