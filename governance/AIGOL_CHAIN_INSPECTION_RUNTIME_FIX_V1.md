# AIGOL_CHAIN_INSPECTION_RUNTIME_FIX_V1

## Status

Certified runtime fix milestone.

`AIGOL_CHAIN_INSPECTION_RUNTIME_FIX_STATUS = CERTIFIED`

## Root Cause

`show-latest-chain` previously coupled operator inspection to mandatory
append-only reconstruction report persistence.

The CLI derived a deterministic report directory from command, chain identity
or `LATEST`, and `created_at`. Repeated invocation with the same inputs reused
the same report directory, and unified replay reconstruction failed closed when
the existing report artifact
`000_unified_replay_reconstruction_recorded.json` was present.

## Runtime Implementation

The fix separates pure inspection from persisted reconstruction evidence.

Implemented behavior:

- unified replay reconstruction entrypoints now accept `persist_report`;
- existing default runtime behavior remains persisted for direct runtime callers;
- chain inspection CLI calls reconstruction with `persist_report=False`;
- default `show-*` commands construct deterministic in-memory reports without
  writing report artifacts;
- source replay remains read-only;
- append-only guarantees remain unchanged for governance chains and explicit
  persisted reconstruction reports.

## Reused Components

Reused without changing their authority model:

- replay wrapper scanning;
- wrapper hash validation;
- artifact hash validation;
- canonical chain selection;
- reference continuity checks;
- unified reconstruction report schema;
- chain inspection renderer;
- fail-closed operator result wrapper.

## Valid Replay Artifacts

Existing persisted artifacts remain valid:

- `000_unified_replay_reconstruction_recorded.json`;
- `001_unified_replay_reconstruction_returned.json`.

They are still produced when direct runtime callers use persisted
reconstruction mode. Operator `show-*` commands no longer require those
artifacts.

## Report Generation Model

Default operator inspection is ephemeral and in-memory.

Inspection artifacts should not exist for default `show-*` commands. Persisted
inspection evidence remains useful, but it must be explicit and append-only.

## Auditability Model

Auditability is preserved through:

- deterministic report content;
- report hash in returned operator output;
- replay-visible source artifact hashes;
- optional persisted reconstruction reports for explicit audit evidence.

Repeatability is preserved because default inspection no longer depends on
creating unique runtime artifacts.

## Authority Boundaries

The fix does not:

- mutate source replay;
- weaken append-only writes;
- create execution requests;
- dispatch workers;
- invoke workers;
- mutate governance;
- introduce new authority.

## Validation Results

Validation passed:

- focused chain inspection and unified reconstruction tests;
- direct repeated `show-latest-chain` execution from a replay workspace;
- JSON certification validation;
- whitespace check.

## Commit Message

`Certify repeatable read-only chain inspection`

## Final Classification

AIGOL_CHAIN_INSPECTION_RUNTIME_FIX_STATUS = CERTIFIED
