# Governance Primitive Replay Continuity Normalization Evidence V1

Status: replay-safe normalization evidence.

## Evidence Summary

Replay and continuity semantics were normalized across the existing bounded preview and test primitives.

The normalization introduces a shared helper:

- `runtime/governance/primitive_replay.py`

The helper centralizes:

- canonical JSON serialization;
- deterministic hashing;
- replay identity construction;
- deterministic result hash construction.

## Normalized Fields

Both preview and test primitive outputs expose:

- `primitive_id`
- `request_hash`
- `command_hash`
- `scope_hash`
- `replay_lineage`
- `deterministic_hash`

## Boundedness Evidence

The normalization does not alter allowed commands.

Preview remains prepared-command only:

- `uvicorn sapianta_system.sapianta_product.main:app --host 127.0.0.1 --port 8010`
- `server_started: false`

Test execution remains prepared-command only:

- `pytest tests/test_governed_preview_runtime.py`
- `executed: false`

## Continuity Evidence

Added validation:

- `tests/test_governance_primitive_replay_continuity.py`

The tests verify:

- shared canonical replay fields;
- visible lineage and scope hashes;
- distinct non-execution markers.

## Explicit Limitations

This normalization does not:

- add a new primitive;
- execute commands;
- start servers;
- run tests through helpers;
- deploy software;
- create orchestration;
- expand operational authority.

