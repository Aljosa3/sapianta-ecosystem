# SEMANTIC_CONTEXT_DIFF_V1

Status: read-only deterministic semantic context change and boundary delta visibility layer.

Scope: replay-visible semantic context diffing across two explicit artifact sets.

## Purpose

`SEMANTIC_CONTEXT_DIFF_V1` compares two semantic context states or cognition artifact sets and reports explicit governance-relevant semantic changes over time.

It reports:

- semantic deltas
- boundary deltas
- continuity deltas
- ambiguity deltas
- authority deltas
- added constraints
- removed constraints
- unchanged anchors

## Diff Types

Supported diff types:

- `semantic_constraint_added`
- `semantic_constraint_removed`
- `semantic_boundary_changed`
- `ambiguity_state_changed`
- `continuity_anchor_changed`
- `authority_boundary_changed`
- `governance_scope_changed`
- `replay_continuity_changed`
- `admissibility_boundary_changed`
- `unknown_delta`

## Delta States

Supported states:

- `NO_CHANGE`
- `CHANGE_DETECTED`
- `UNKNOWN`
- `BOUNDARY_DRIFT_RISK`
- `CONTINUITY_DELTA`
- `INVALID_DIFF_INPUT`

## Rules

The diff compares explicit artifact fields only.

Missing evidence becomes `UNKNOWN`.

The diff does not use:

- hidden semantic inference
- semantic interpretation
- semantic optimization
- semantic repair
- probabilistic matching
- fuzzy reasoning

## CLI Observability

The CLI command is:

```bash
aigol cognition semantic-diff --source <artifact_or_directory> --target <artifact_or_directory>
```

Optional flags:

- `--json`
- `--output <path>`
- `--validate`

Writing output is explicit only.

## Governance Guarantees

This layer is read-only, deterministic, replay-visible, governance-safe, and bounded.

It grants no execution authority, orchestration, runtime activation, provider routing, provider activation, semantic repair, ambiguity resolution, autonomous semantic evolution, or executable semantic graph semantics.
