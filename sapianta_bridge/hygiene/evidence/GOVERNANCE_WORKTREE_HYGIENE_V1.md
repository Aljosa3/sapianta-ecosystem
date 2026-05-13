# Governance Worktree Hygiene v1

## Purpose

This evidence artifact establishes deterministic governance worktree hygiene for replay-safe AGOL development.

It distinguishes canonical governance artifacts from transient runtime artifacts before artifacts are allowed into governance lineage.

## Canonical Context

Current canonical milestones:

- `FINALIZE_REPO_WIDE_TEST_COLLECTION_STABILIZATION_V1`
- `AGOL_LAYER_SEPARATION_MODEL_V1`

This milestone does not rewrite history, mutate canonical tags, alter replay references, or remove previous milestone evidence.

## Artifact Classes

### CANONICAL_GOVERNANCE_ARTIFACT

Examples:

- ADRs
- governance manifests
- replay evidence
- deterministic test evidence
- policy evidence
- architecture evidence

### TRANSIENT_RUNTIME_ARTIFACT

Examples:

- `__pycache__`
- `*.pyc`
- `*.pyo`
- `.pytest_cache`
- runtime temp files
- generated runtime noise
- transient logs
- ephemeral execution state
- replay cache noise

### UNKNOWN_ARTIFACT

Anything uncertain.

Unknown artifacts fail closed, require explicit classification, and must not silently enter governance lineage.

## Replay Pollution Rule

Transient runtime artifacts are execution residue. They are not canonical governance evidence.

If transient or unknown artifacts are candidates for governance lineage, hygiene validation must block them and require human review.

## Non-Goals

This milestone does not implement provider abstraction, execution routing, orchestration, runtime optimization, execution envelopes, semantic governance redesign, replay rewriting, history rewriting, tag mutation, or branch restructuring.
