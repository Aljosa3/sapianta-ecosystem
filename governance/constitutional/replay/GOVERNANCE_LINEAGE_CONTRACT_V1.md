# GOVERNANCE_LINEAGE_CONTRACT_V1

Status: CANONICAL GOVERNANCE LINEAGE CONTRACT

## Purpose

This artifact defines governance lineage contracts for replay-safe
evidence.

It does not implement lineage engines or mutation execution.

## Lineage Chain Structure

Governance lineage MUST represent:

- lineage root;
- parent governance event;
- child governance event;
- replay identity;
- evidence hash;
- proposal reference;
- approval reference where applicable;
- promotion reference where applicable;
- rollback reference where applicable;
- certification reference where applicable.

## Parent / Child Relationships

Every child governance event MUST reference its parent lineage.

Parent lineage MUST remain replay-visible.

Child lineage MUST append and MUST NOT rewrite parent evidence.

## Promotion Lineage

Promotion lineage MUST link:

- proposal evidence;
- replay verification evidence;
- approval evidence;
- certification evidence;
- promotion decision evidence;
- rollback compatibility evidence.

Promotion lineage does not grant authority by itself. Authority requires
explicit approval.

## Rollback Lineage

Rollback lineage MUST link:

- promoted evidence;
- rollback trigger;
- rollback decision;
- rollback event evidence;
- post-rollback validation;
- preserved replay history.

Rollback preserves lineage visibility and does not erase promotion
history.

## Replay Lineage Continuity

Replay lineage continuity is valid only when:

- predecessor evidence remains present;
- replay identities are not reused;
- deterministic hashes verify;
- lineage references resolve;
- append-only ordering is preserved.

## Guarantees

- lineage continuity is preserved;
- lineage is never silently rewritten;
- rollback preserves lineage visibility;
- replay lineage remains append-only;
- governance ancestry remains visible.

## Fail-Closed Rule

If lineage cannot be verified:

-> fail closed
-> quarantine evidence
-> block promotion
-> no mutation authority
