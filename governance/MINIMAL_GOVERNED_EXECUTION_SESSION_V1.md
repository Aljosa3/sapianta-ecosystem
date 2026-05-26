# MINIMAL_GOVERNED_EXECUTION_SESSION_V1

## Scope

This milestone introduces the first minimal governed execution session lifecycle for AiGOL.

The session model supports only:

- creating one local governed execution session;
- attaching bounded provider evidence;
- preserving deterministic append-only operation order;
- reconstructing replay-linked session lineage;
- explicitly closing the session.

## Session Fields

The minimal session object contains:

- `session_id`
- `created_at`
- `status`
- `operations`
- `closed_at`
- `evidence_hash`

Allowed statuses are:

- `CREATED`
- `ACTIVE`
- `CLOSED`
- `FAILED`

## Allowed Providers

Provider evidence may be attached only for:

- `readonly_filesystem_provider`
- `readonly_http_get_provider`
- `metadata_inspection_provider`

## Guarantees

- Single-session local lifecycle only.
- Append-only operation tracking.
- Deterministic operation ordering.
- Replay-linked operation hash chain.
- Deterministic session evidence hash.
- Explicit `close_session()`.
- Fail-closed invalid transitions.
- Duplicate closure rejection.
- Attach-after-close rejection.
- Immutable provider evidence after attach.

## Non-Goals

- Agent framework.
- Workflow engine.
- Orchestration platform.
- Multi-step autonomous runtime.
- Distributed execution system.
- Autonomous planning.
- Retries.
- Async execution.
- Concurrent sessions.
- Background workers.
- Scheduling.
- Vector memory.
- Semantic reasoning.
- Agent loops.
- Execution delegation.

## Boundary

This session lifecycle does not invoke providers, plan work, schedule work, retry work, delegate execution, persist background state, or coordinate multiple sessions. It records bounded provider evidence that already exists and makes the session lineage replay-reconstructable.

## Certification

`MINIMAL_GOVERNED_EXECUTION_SESSION_V1` certifies bounded local session lifecycle semantics with replay-linked execution lineage, append-only operation semantics, fail-closed transitions, and no orchestration, autonomous planning, or agent runtime.
