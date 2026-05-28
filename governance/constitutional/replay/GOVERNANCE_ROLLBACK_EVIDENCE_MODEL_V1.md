# GOVERNANCE_ROLLBACK_EVIDENCE_MODEL_V1

Status: CANONICAL GOVERNANCE ROLLBACK EVIDENCE MODEL

## Purpose

This artifact defines rollback evidence requirements for governance
replay evidence.

It does not implement rollback execution.

## Required Rollback Fields

### rollback_id

Purpose: canonical identity for rollback evidence.

Immutability: immutable after rollback evidence creation.

Replayability: replay must reproduce identity from canonical evidence.

Lineage: links to affected proposal, promotion, and replay lineage.

### rollback_reason

Purpose: explains why rollback is required.

Immutability: appended as evidence and not rewritten.

Replayability: must be visible in replay manifest.

Lineage: preserved in rollback lineage.

### rollback_scope

Purpose: defines affected governance or runtime scope.

Immutability: scope changes require new evidence.

Replayability: scope classification must be reproducible.

Lineage: links to constitutional scope and affected evidence.

### rollback_trigger

Purpose: identifies failure, instability, replay loss, approval
violation, or protected-layer issue.

Immutability: immutable after event evidence.

Replayability: trigger evidence must replay deterministically.

Lineage: references triggering evidence.

### rollback_lineage_reference

Purpose: binds rollback to prior promotion and governance lineage.

Immutability: cannot be edited to hide ancestry.

Replayability: referenced lineage must be replay-visible.

Lineage: append-only rollback chain.

### rollback_evidence_hash

Purpose: deterministic hash of rollback evidence.

Immutability: immutable after creation.

Replayability: hash must reproduce from canonical serialization.

Lineage: referenced by post-rollback validation.

### rollback_certification_status

Purpose: records rollback evidence certification state.

Immutability: status changes append; prior state is not rewritten.

Replayability: certification evidence must be reproducible.

Lineage: visible in rollback and governance lineage.

## Rollback Guarantees

- rollback evidence is immutable;
- rollback evidence is traceable;
- rollback evidence is replayable;
- rollback preserves lineage visibility;
- rollback events append rather than erase.

## Mandatory Rollback Conditions

Rollback evidence is mandatory for failed evolution, unstable behavior,
loss of replayability, approval boundary violation, or protected-layer
mutation.
