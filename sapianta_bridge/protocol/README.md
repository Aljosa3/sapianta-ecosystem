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

## Why Execution Is Excluded

Execution transport comes after protocol stability. This milestone prevents artifact drift, hidden state transitions, non-replayable coordination, and uncontrolled AI execution paths before any bridge listener or runtime invocation exists.

## Future Milestones

- Bridge transport
- Reflection layer
- Governance orchestration
- Bounded autonomy

