# First Real Worker Recommendation V1

Status: planning-only worker candidate evaluation.

## Evaluated Candidates

### Runtime Inspection Worker

Strengths:

- Maps directly to frozen `READ_ONLY_RUNTIME_INSPECTION`.
- Read-only.
- No filesystem path policy needed.
- Smallest execution surface.
- Best first proof of worker identity, authorization gate, replay mapping, and termination evidence.

Risks:

- Provides limited practical utility compared with filesystem inspection.

Assessment: recommended first worker attachment.

### Filesystem Read-Only Worker

Strengths:

- Useful and already aligned with `FILESYSTEM_READ_ONLY_INSPECTION`.
- Still read-only.

Risks:

- Requires path normalization, allowed-path enforcement, symlink/relative-path handling, and stronger boundary pressure testing.
- Slightly larger surface than runtime inspection.

Assessment: second worker candidate after runtime inspection worker proves attachment boundary.

### CLI Read-Only Worker

Strengths:

- Could inspect runtime/system state.

Risks:

- CLI execution risks shell semantics, command injection, subprocess behavior, environment leakage, and authority confusion.
- Not appropriate for first real worker attachment.

Assessment: defer.

### API Query Worker

Strengths:

- Useful for external data lookup in future.

Risks:

- Introduces network/API surface, credentials, rate limits, response ambiguity, provider failures, and replay capture complexity.
- Not appropriate before worker identity and replay mapping are proven locally.

Assessment: defer.

## Recommendation

Recommended first worker: runtime inspection worker.

## Why This Is Smallest

Runtime inspection worker exercises:

- worker identity
- AiGOL authorization evidence
- capability binding
- worker execution-only boundary
- replay-visible worker result
- explicit termination

without introducing:

- filesystem mutation
- path ambiguity
- shell execution
- network execution
- API execution
- orchestration
- memory

## Implementation Readiness

`REAL_WORKER_ATTACHMENT_IMPLEMENTATION_READY`: `MOSTLY_READY_WITH_CONSTRAINTS`

Ready to plan as a runtime-inspection-only worker. Not ready for filesystem, CLI, API, or mutating worker attachment as the first step.
