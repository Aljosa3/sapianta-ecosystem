# Attachment Readiness Assessment V1

Status: analysis-only readiness classification.

## Assessment Scale

Readiness classifications:

- `READY`: all core attachment prerequisites are present and only execution of the milestone remains.
- `MOSTLY_READY`: core semantics are stable; a narrow binding and validation layer remains.
- `PARTIALLY_READY`: foundational semantics exist, but explicit attachment boundary work remains.
- `NOT_READY`: baseline semantics are not yet stable enough for attachment.

## REAL_LLM_ATTACHMENT_READINESS

Classification: `MOSTLY_READY`

Reason:

- The frozen baseline already treats cognition output as untrusted proposal input.
- AiGOL governance, validation, authorization, and replay are already mandatory.
- Historical external LLM attachment and provider artifacts exist.
- The remaining work is a freeze-compatible real provider binding into the operator flow with provider identity, raw response replay, normalization, and pressure tests.

Blocking gaps before attachment:

- deterministic provider identity contract
- raw response replay mapping inside the frozen operator path
- single-shot session ordering rules
- provider output normalization into the existing proposal bridge
- fail-closed tests for malformed and authority-escalating provider output

Shortest safe next step:

Create `REAL_LLM_ATTACHMENT_V1` as a single-provider, proposal-only, replay-visible attachment that produces existing bridge-compatible proposal input and cannot authorize or execute.

## REAL_WORKER_ATTACHMENT_READINESS

Classification: `PARTIALLY_READY`

Reason:

- The frozen baseline already preserves worker execution-only semantics.
- Authorization-before-execution and read-only capability boundaries are stable.
- The current worker is still effectively in-process capability execution, not a separately identified worker attachment boundary.
- A real worker requires explicit worker identity, adapter boundary, capability binding, replay mapping, and isolation testing.

Blocking gaps before attachment:

- deterministic worker identity envelope
- worker adapter requiring AiGOL authorization evidence
- capability binding limited to frozen read-only capabilities
- worker input/output replay mapping
- hidden state and self-authorization rejection tests

Shortest safe next step:

Create `REAL_WORKER_ATTACHMENT_V1` as one read-only worker adapter with explicit worker identity, no self-authorization, no new capability, and replay-visible input/output/termination evidence.

## Combined Readiness

The shortest safe path is:

1. Attach real LLM proposal source first, because it can remain non-executing.
2. Pressure-test proposal-only behavior against the frozen operator flow.
3. Attach one real read-only worker boundary after authorization and replay mapping are explicit.

This order preserves constitutional clarity: proposal attachment before worker attachment, and both remain governed by AiGOL.
