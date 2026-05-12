# Finalize BRIDGE_PROTOCOL_V0_1

## Finalized Scope

`BRIDGE_PROTOCOL_V0_1` finalizes `SAPIANTA CODEX BRIDGE PROTOCOL v0.1` as a deterministic protocol substrate for governed AI coordination.

Finalized artifacts include:

- Canonical protocol schemas.
- Fail-closed validation contracts.
- Lifecycle state machine.
- Replay-safe SHA256 hashing.
- Lineage validation.
- Protocol manifest.
- Example artifacts.
- Protocol validation tests.

## Locked Behaviors

The following behaviors are locked for this milestone:

- Protocol version is `0.1`.
- Validation is fail-closed.
- Unknown artifact types are rejected.
- Unknown enum values are rejected.
- Invalid protocol versions are rejected.
- Missing lineage is rejected.
- Missing or invalid hashes are rejected where schema requires hashes.
- Invalid lifecycle transitions are rejected.
- `CLOSED` and `QUARANTINED` are terminal.
- Failure states require evidence.
- `next_task_proposal.json` must set `allowed_to_execute_automatically` to `false`.

## Validation Summary

Finalization acceptance evidence records successful validation for:

- `pytest tests/test_protocol_validator.py tests/test_lifecycle.py tests/test_hashing.py tests/test_lineage.py`
- `python -m py_compile` over protocol modules.
- `git diff --check`.
- `git -C sapianta_system diff --check`.

## Replay Guarantees

The protocol uses canonical JSON serialization with stable key ordering and compact separators. SHA256 hashes are deterministic across runs. Self-hash fields are omitted from their own hash input to avoid recursive hashes while preserving replay safety.

## Deterministic Guarantees

The milestone contains no execution transport, subprocess invocation, external runtime dependency, background listener, service process, network transport, or runtime persistence. Validation and hashing are deterministic over supplied artifacts.

## Fail-Closed Guarantees

Malformed artifacts are not repaired. Validation fails closed on invalid JSON, invalid protocol versions, missing lineage, invalid hashes, unknown lifecycle states, invalid transitions, malformed schemas, unsupported artifact types, and unknown enum values.

## Excluded Capabilities

This milestone excludes:

- Execution transport.
- Bridge listener.
- Codex subprocess execution.
- Runtime orchestration.
- Reflection automation.
- Recursive autonomy.
- Auto execution.
- Auto approval.
- Auto repair.
- Auto merge.
- Auto push.
- Governance mutation.

## Future Milestone Dependency Chain

```text
BRIDGE_PROTOCOL_V0_1
-> SCHEMA_VALIDATOR_INTEGRATION_V1
-> CODEX_BRIDGE_TRANSPORT_MVP_V1
-> REFLECTION_LAYER_V1
-> HUMAN_APPROVAL_QUEUE_V1
-> BOUNDED_AUTONOMY_V1
```

Future milestones must preserve the finalized protocol substrate unless a new explicitly governed milestone reopens the protocol behavior.

