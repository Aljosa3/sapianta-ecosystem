# SAPIANTA CODEX BRIDGE PROTOCOL v0.1

This package defines the deterministic protocol substrate for governed AI coordination in SAPIANTA.

It formalizes artifact schemas, lifecycle states, validation contracts, replay-safe hashes, lineage references, and evidence envelopes before any execution transport exists.

## Non-Goals

v0.1 does not execute Codex, spawn subprocesses, run recursive loops, auto-repair, auto-merge, auto-push, orchestrate runtime work, or mutate governance. It only validates protocol artifacts.

## Artifact Flow

```text
task.json
-> validation
-> result.json
-> analysis_context.json
-> interpretation
-> next_task_proposal.json
```

The protocol defines evidence and state. Execution transport is intentionally excluded.

## Schemas

- `task.json`: bounded request envelope with target paths, allowed and forbidden operations, validation requirements, approval requirements, and lineage.
- `result.json`: deterministic result envelope with file changes, tests, errors, warnings, diff summary, artifact hashes, and lineage.
- `analysis_context.json`: interpretation context with architectural impact, governance impact, risk analysis, opportunities, recommended next milestone, hashes, and lineage.
- `next_task_proposal.json`: bounded proposal envelope for follow-up work. `allowed_to_execute_automatically` must always be `false` in v0.1.

## Lifecycle

Canonical success path:

```text
CREATED -> VALIDATED -> SENT_TO_CODEX -> EXECUTING -> RESULT_RECEIVED
-> ANALYSIS_CONTEXT_CREATED -> INTERPRETED -> NEXT_TASK_PROPOSED -> CLOSED
```

Failure states are explicit and evidence-bound:

```text
VALIDATION_FAILED, EXECUTION_FAILED, TEST_FAILED, RESULT_MISSING,
CONTEXT_MISSING, ESCALATED, BLOCKED, QUARANTINED
```

`CLOSED` and `QUARANTINED` are terminal. Failure states cannot silently continue.

## Hashing Rules

All hashes use SHA256 over canonical JSON with stable key ordering and compact separators. Self-hash fields are omitted from the hash input to avoid recursive hashes while preserving deterministic replay.

## Lineage Rules

Lineage is schema-only in v0.1. IDs must be explicit and non-empty unless a schema permits `null` for a root artifact reference. There is no graph database and no runtime persistence.

## Fail-Closed Principles

Validation fails closed for invalid JSON, invalid protocol versions, missing lineage, missing or malformed hashes, unknown lifecycle states, invalid transitions, malformed schemas, unsupported artifact types, and unknown enum values.

Malformed artifacts are never silently repaired.

## Validator CLI

The protocol validator is available as a deterministic command-line gate:

```bash
python -m sapianta_bridge.protocol.cli validate path/to/artifact.json
```

Exit codes:

- `0`: artifact is valid and allowed to continue.
- `1`: artifact is invalid and must not continue.
- `2`: internal validator failure or invalid CLI usage.

The CLI automatically classifies supported protocol artifacts, validates schema, hashes, lineage, protocol version, and lifecycle state fields, then emits deterministic JSON.

## Enforcement Lifecycle

`enforcement.py` wraps the schema validator and lifecycle validator into a mandatory governance gate. An artifact may continue only if it is a known supported artifact, schema-valid, hash-valid where hashes are required, lineage-valid, protocol-version-valid, and lifecycle-valid.

Invalid, malformed, unknown, or uncertain artifacts are blocked with `required_state: "QUARANTINED"`.

## Quarantine Philosophy

`quarantine.py` preserves malformed or governance-unsafe artifacts without repair. Each quarantine record stores the original artifact bytes and a `quarantine.json` envelope containing a quarantine ID, timestamp, artifact path, reason, validation errors, and `sha256:` source hash.

Quarantine categories are:

- `malformed`
- `invalid_hash`
- `invalid_lineage`
- `invalid_lifecycle`
- `unknown_artifact`

Quarantine exists so future execution layers cannot bypass deterministic protocol contracts. Quarantined artifacts are isolated, not fixed, and must not continue.

## Why Execution Is Excluded

Execution transport comes after protocol stability. This milestone prevents artifact drift, hidden state transitions, non-replayable coordination, and uncontrolled AI execution paths before any bridge listener or runtime invocation exists.

## Future Milestones

- Bridge transport
- Reflection layer
- Governance orchestration
- Bounded autonomy
