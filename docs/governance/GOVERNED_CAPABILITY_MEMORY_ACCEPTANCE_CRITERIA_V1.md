# Governed Capability Memory Acceptance Criteria V1

Status: finalized acceptance criteria.

Subsystem:
`GOVERNED_CAPABILITY_MEMORY_V1`

## Acceptance Requirements

The subsystem is accepted only if:

- operational trust remains bounded;
- approvals remain replay-visible;
- escalation semantics remain strict;
- revocation remains deterministic;
- capability scope remains locked;
- replay-safe lineage remains preserved;
- deterministic evaluation hashes remain stable;
- operational acceleration improves without autonomy drift.

## Capability Acceptance

`LOCALHOST_PREVIEW_RUNTIME_V1` is accepted only when:

- host is `127.0.0.1`;
- runtime is `uvicorn`;
- lifecycle is `start -> validate -> stop`;
- execution is temporary;
- visual validation is in scope;
- deployment semantics are absent;
- persistence semantics are absent;
- public exposure is absent;
- background execution is absent.

## Rejection and Escalation Conditions

The subsystem must escalate or reject when:

- capability ID is unknown;
- capability is revoked;
- host changes;
- port changes;
- runtime changes;
- lifecycle changes;
- persistence appears;
- deployment semantics appear;
- background execution appears;
- public network exposure appears;
- mutation scope expands.

## Forbidden Acceptance Conditions

The subsystem is not accepted if it introduces:

- autonomous runtime execution;
- deployment automation;
- daemon persistence;
- unrestricted shell execution;
- unrestricted operational inheritance;
- self-authorizing permissions;
- orchestration engines;
- weakened replay visibility;
- weakened revocation semantics.

## Current Acceptance State

Acceptance state:
`ACCEPTED_BOUNDED_CAPABILITY_MEMORY`

Reason:
The registry is deterministic, read-only, scope-locked, escalation-aware, and covered by targeted tests.

