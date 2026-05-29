# Real LLM Attachment Gaps V1

Status: analysis-only gap record.

## Readiness Context

The frozen baseline already supports proposal-only cognition semantics and treats cognition output as untrusted proposal input.

Existing historical artifacts indicate prior work around:

- external LLM attachment boundaries
- live external LLM provider boundaries
- provider-agnostic raw response capture
- deterministic normalization
- replay-visible inference lineage

The remaining gap is not the absence of all attachment concepts. The remaining gap is integrating one real external LLM attachment into the frozen `FIRST_USEFUL_AIGOL_V1` operator flow without weakening the frozen invariant.

## Missing Before Real LLM Attachment

### Freeze-Compatible Provider Binding

A real LLM provider must be bound to the frozen operator path as a proposal source only.

It must not bypass the proposal bridge, AiGOL validation, authorization, worker execution boundary, or replay recording.

### Provider Identity Contract

A real attachment needs deterministic provider identity fields:

- provider id
- provider name
- model name
- invocation id
- response id
- created timestamp
- attachment boundary version

### Raw Response Replay Mapping

The raw provider response must be replay-visible before normalization.

Required replay stages:

- provider invocation envelope
- raw provider response
- response hash
- normalized proposal
- validation result
- authorization result

### Proposal Normalization Compatibility

The provider output must normalize into the existing proposal input shape expected by the proposal bridge.

Malformed, incomplete, ambiguous, authority-escalating, or unsupported-capability proposals must fail closed.

### Session and Ordering Constraint

The real LLM attachment needs deterministic ordering within one operator flow.

It must not introduce hidden sessions, streaming continuation, retries, async execution, memory carryover, or recursive proposals.

### Attachment Boundary Tests

Before real attachment is accepted, tests should pressure:

- malformed provider output
- missing provider identity
- raw response hash mismatch
- unsupported capability proposal
- hidden continuation language
- execution-authority claims
- replay ordering mismatch
- provider timeout or empty response represented as deterministic failure

## Not Missing

The following are already conceptually present in the frozen baseline:

- proposal-only treatment
- untrusted proposal normalization
- AiGOL validation
- AiGOL authorization
- read-only execution boundary
- fail-closed rejection
- replay-derived governed return

## Real LLM Attachment Readiness

`REAL_LLM_ATTACHMENT_READINESS`: `MOSTLY_READY`

Reason: the constitutional and runtime semantics are already aligned for proposal-only attachment, and historical provider artifacts exist. The missing work is a narrow freeze-compatible binding from one real provider response into the frozen operator path with replay mapping and pressure validation.
