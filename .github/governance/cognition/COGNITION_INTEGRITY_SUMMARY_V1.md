# COGNITION_INTEGRITY_SUMMARY_V1

Status: unified read-only cognition integrity audit summary.

Scope: deterministic cognition health rollup across existing cognition integrity artifacts.

## Purpose

`COGNITION_INTEGRITY_SUMMARY_V1` consolidates the cognition integrity stack into one replay-visible governance-safe audit view.

It answers:

- whether the cognition stack is structurally healthy
- whether governance guarantees remain intact
- whether semantic continuity is stable, degraded, or unknown
- whether replay and lineage visibility are coherent
- whether cognition subsystem topology is valid
- whether lifecycle transitions are structurally valid
- whether authority boundaries remain bounded

## Inputs

The summary consolidates:

- `BOUNDED_COGNITION_STATE_ENVELOPE_V1`
- `SEMANTIC_REPLAY_CONTINUITY_CHECK_V1`
- `COGNITION_REGISTRY_V1`
- `COGNITION_REGISTRY_TOPOLOGY_REPORT_V1`
- `COGNITION_LIFECYCLE_MODEL_V1`

Missing live semantic evidence is reported as `UNKNOWN`, not inferred.

## Health States

Supported integrity states:

- `HEALTHY`
- `HEALTHY_WITH_UNKNOWN_CONTEXT`
- `DEGRADED`
- `INVALID`

`HEALTHY_WITH_UNKNOWN_CONTEXT` means the structural cognition stack is valid, but live semantic replay evidence is absent or warning-bearing.

## Non-Goals

This milestone does not create:

- execution authority
- orchestration
- autonomous cognition
- planning
- runtime cognition execution
- provider routing
- semantic reasoning
- hidden inference
- runtime activation
- cognition scheduling
- self-modifying cognition
- dynamic repair behavior
- continuity repair

## Governance Guarantees

The summary explicitly preserves:

- no execution authority
- no orchestration
- no autonomous cognition
- no autonomous continuation
- no planning authority
- no runtime cognition execution
- no provider routing
- no provider activation
- no semantic reasoning
- no hidden inference
- no runtime activation
- no cognition scheduling
- no self-modifying cognition
- no dynamic repair behavior
- no continuity repair

## CLI Observability

The CLI command is:

```bash
aigol cognition integrity
```

Optional flags:

- `--input <artifact_or_directory>`
- `--json`
- `--output <path>`
- `--validate`

Writing output is explicit only. Validation checks structural integrity and no-authority boundaries.

## Replay Visibility

The summary includes:

- component statuses
- source hashes
- health summary
- audit findings
- unknowns
- deterministic `integrity_summary_hash`

The artifact is audit evidence only. It does not repair continuity, mutate evidence, or activate cognition behavior.
