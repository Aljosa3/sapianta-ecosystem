# External Worker Architecture Impact V1

Status: external Worker architecture impact review.

## Architecture Impact Classification

`EXTERNAL_WORKER_ARCHITECTURE_IMPACT`: `MINOR_ADJUSTMENTS_REQUIRED`

## Reason

No new constitutional architecture is required, but first implementation needs a small external Worker adapter surface because no external Worker adapter currently exists.

This is adapter mechanics, not a new AiGOL authority model.

## Required Adapter Mechanics

The first external Worker attachment needs:

- worker identity envelope
- authorized request handoff
- deterministic capability binding
- worker execution request artifact
- worker result evidence
- worker termination evidence
- replay reconstruction for worker attachment evidence
- fail-closed handling for worker unavailable, timeout, corruption, replay mismatch, capability mismatch, and identity mismatch

## Not Required

The first external Worker attachment does not require:

- new governance concepts
- new authority concepts
- new constitutional concepts
- new capability classes
- worker registry
- worker discovery
- worker selection
- worker orchestration
- worker memory
- worker autonomy
- mutation authority

## Runtime Impact

The runtime impact should be narrowly scoped to an external Worker adapter that delegates only to already authorized read-only/inspection execution.

It should not alter:

- proposal bridge semantics
- authorization model
- provider model
- replay source-of-truth semantics
- read-only capability boundaries
- frozen invariant

## Readiness Constraint

The first external Worker should be a single explicit Worker attachment, not the beginning of a Worker ecosystem.

