# Governance Primitive Replay Continuity Normalization V1

Status: bounded replay semantics normalization.

Purpose: normalize replay and continuity semantics across existing governed primitives without introducing new operational authority.

Covered primitives:

- `GOVERNED_PREVIEW_RUNTIME_EXECUTION_V1`
- `GOVERNED_TEST_EXECUTION_V1`

Supporting helper:

- `runtime/governance/primitive_replay.py`

## Normalized Replay Vocabulary

Existing executable governance primitives should expose:

- `primitive_id`
- `request_hash`
- `command_hash`
- `scope_hash`
- `replay_lineage`
- `deterministic_hash`

These fields make primitive outputs comparable across repeated evaluations.

## Continuity Semantics

Continuity means:

- primitive identity remains stable;
- scope identity remains stable;
- command preparation remains deterministic;
- lineage references remain visible;
- non-execution status remains explicit;
- forbidden boundary checks remain visible.

## Boundedness Preservation

Normalization does not authorize:

- command execution;
- server start;
- test execution;
- deployment;
- orchestration;
- daemon persistence;
- public binding;
- production mutation;
- arbitrary shell execution.

## Implementation Boundary

`primitive_replay.py` centralizes deterministic hash and replay identity construction.

It does not execute commands. It does not evaluate policy. It does not create new capabilities. It only provides stable replay metadata for existing bounded primitives.

## Acceptance Condition

Normalization is acceptable when:

- existing primitive tests still pass;
- preview and test primitives share canonical replay fields;
- helpers remain non-executing;
- scope hashes remain primitive-specific;
- runtime behavior does not change.

