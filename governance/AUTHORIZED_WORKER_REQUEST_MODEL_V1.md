# AUTHORIZED_WORKER_REQUEST_MODEL_V1

## Status

AUTHORIZED_WORKER_REQUEST_STATUS = CERTIFIED

## Purpose

This milestone certifies the transition:

```text
Authorization Artifact
-> Authorized Worker Request
```

without introducing worker execution, execution runtime, dispatch runtime,
orchestration, planning, or reflection.

## Constitutional Invariant

LLM proposes.

AiGOL governs.

Worker executes.

Replay records.

## Core Answer

The minimal governed object that a worker may legally receive is:

```text
AUTHORIZED_WORKER_REQUEST
```

It is derived from a valid governed authorization artifact and contains only
bounded worker target, scope, lineage, and request metadata.

## Authority Questions

Can authorization artifact execute work?

No.

Can authorized worker request execute work?

No.

Can worker receive raw proposal?

No.

Can worker receive raw authorization artifact?

No.

Can worker receive only authorized worker request?

Yes.

Can authorized request exceed authorization scope?

No.

## Minimal Admissible Request

Required fields:

- request_id
- authorization_id
- worker_id
- authorized_scope
- request_timestamp
- request_hash

Additional required lineage:

- proposal_reference
- authorization_hash
- capability_binding
- replay_reference

## Boundary

An authorized worker request is not execution.

It is not dispatch.

It is not orchestration.

It is not worker invocation.

It is the minimum legal handoff object a worker may receive before execution
boundary validation.

## Replay Requirements

Replay must reconstruct:

- proposal
- authorization
- authorized request
- worker target
- scope
- request lineage

## Fail-Closed Requirements

The request model fails closed on:

- missing authorization
- scope mismatch
- worker mismatch
- invalid request lineage
- invalid request metadata
- authorization not found

## Authority Preservation

Provider authority = none.

Proposal authority = none.

Authorization authority = bounded.

Authorized request authority = bounded.

Worker authority = execution only.

No authority escalation is permitted.

## Final Certification

AUTHORIZED_WORKER_REQUEST_STATUS = CERTIFIED

Workers receive only governed authorized requests and never raw provider output,
raw proposals, or raw authorization artifacts.
