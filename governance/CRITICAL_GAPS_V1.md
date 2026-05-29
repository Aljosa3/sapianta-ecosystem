# Critical Gaps V1

Status: must-have gaps before first useful AiGOL.

## Critical Gap 1: Operator Invocation Boundary

The frozen runtime exists, but first useful AiGOL needs a minimal operator-facing invocation boundary.

Required shape:

- one explicit command or callable entrypoint
- accepts one human prompt
- selects only existing read-only capability targets
- writes replay evidence to an explicit location
- returns a governed result summary
- fails closed on ambiguity

This must not become orchestration, autonomous routing, or multi-step planning.

## Critical Gap 2: Governed Result Readability

The runtime returns structured evidence, but first useful operation needs a concise operator-readable result.

Required shape:

- accepted or rejected status
- capability used
- replay path or replay identifier
- short evidence summary
- rejection reason when failed
- authority boundary reminder

This is presentation of existing evidence, not new reasoning.

## Critical Gap 3: Replay Evidence Retrieval

Replay is central, but first useful operation needs a bounded way to retrieve or summarize replay evidence.

Required shape:

- read-only replay summary
- deterministic ordering
- hash verification result
- operator-level and bridge-level lineage visibility
- no adaptive search or semantic indexing

This should remain lookup-oriented and non-autonomous.

## Critical Gap 4: Frozen Epoch Pressure Validation

The frozen epoch should be pressure-tested before expansion.

Required scenarios:

- unsupported capability request
- unauthorized proposal
- malformed prompt
- hidden continuation attempt
- forbidden filesystem path
- replay hash corruption
- replay ordering corruption

This confirms stable failure behavior before new capability work.

## Critical Gap 5: Minimal Usage Documentation

First useful AiGOL needs a short operator guide that explains how to use the frozen read-only flow and how to interpret governed result evidence.

Required shape:

- one happy path
- one rejected path
- replay location explanation
- explicit non-goals
- no promise of general autonomy

## Critical Path Recommendation

Build next:

```text
minimal operator CLI / invocation wrapper
-> governed result summary
-> replay summary command
-> frozen epoch pressure tests
-> short operator usage guide
```
