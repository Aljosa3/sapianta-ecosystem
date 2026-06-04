# AIGOL_REPLAY_INSPECTION_REUSE_PLAN_V1

## Status

Review-only reuse plan.

## Reuse The Reconstruction Engine

Keep:

- replay wrapper scanning;
- wrapper hash validation;
- artifact hash validation;
- chain selection;
- reference continuity validation;
- report schema.

## Split Read And Persist Paths

Introduce two modes in a future implementation milestone:

- pure inspection mode: reconstruct and return a report without filesystem
  writes;
- persisted evidence mode: write append-only report artifacts with explicit
  operator intent.

## Preserve Append-Only Semantics

Do not weaken `write_json_immutable` or append-only runtime guarantees.

Instead:

- avoid writes in default show mode;
- use unique report identity for persisted mode;
- optionally return an existing matching report if idempotent replay evidence is
  explicitly certified.

## Reuse CLI Rendering

Keep `render_chain_inspection_summary`, but add fields:

- `source_replay_read_only`;
- `inspection_report_persisted`;
- `report_persistence_mode`;
- `report_collision_detected`;
- `operator_recovery_hint`.

## Reuse Existing Tests

Extend current tests rather than replacing them:

- keep source replay immutability tests;
- add repeat invocation tests;
- add pure inspection no-write tests;
- add persisted report unique-id tests;
- add collision diagnostics tests.

## Non-Reuse Boundary

Do not reuse the current default mandatory report persistence behavior for OCS
operator transparency.
