# GOVERNANCE_REPLAY_EVIDENCE_SCHEMA_V1

Status: CONSTITUTIONAL REPLAY EVIDENCE FOUNDATION ONLY

Layer: Constitutional Governance Replay

Principle: Deterministic Governance Evidence Before Adaptive Replay Authority

## Purpose

This specification defines the canonical governance replay evidence
schema for SAPIANTA/AiGOL before adaptive runtime governance,
replay-driven mutation authority, or replay-triggered activation exists.

This phase is governance-only, schema-only, replay-only,
constitutional-only, documentation/evidence-only, and freeze-only.

It does not implement runtime replay engines, governance mutation,
adaptive governance, governance orchestration, autonomous replay
interpretation, mutation execution, runtime authority, or
replay-triggered activation.

## Governance Replay Evidence Principles

- replay evidence must be deterministic;
- replay evidence must be append-only;
- governance lineage must be traceable;
- replay identity must be canonical;
- evidence mutation is prohibited;
- replay visibility is mandatory;
- rollback traceability is mandatory;
- promotion traceability is mandatory.

Constitutional distinctions:

- replay != execution;
- lineage != authority;
- evidence != activation;
- replay verification != mutation approval.

## Canonical Replay Evidence Structure

Governance replay evidence MUST contain the following fields in
canonical order:

1. `governance_id`
2. `proposal_id`
3. `replay_id`
4. `lineage_reference`
5. `approval_reference`
6. `rollback_reference`
7. `promotion_reference`
8. `evidence_bundle_hash`
9. `deterministic_hash`
10. `certification_status`
11. `mutation_class`
12. `quarantine_status`
13. `timestamp_reference`
14. `constitutional_scope`

## Field Contracts

### governance_id

Purpose: identifies the governed evidence domain.

Immutability rules: immutable after evidence creation.

Replay requirements: must resolve to the same governance domain during
replay.

Validation requirements: non-empty deterministic identifier.

Lineage requirements: must be preserved across child evidence.

### proposal_id

Purpose: binds evidence to the governance proposal under review.

Immutability rules: immutable after evidence creation.

Replay requirements: must be reproducible from proposal evidence.

Validation requirements: must match proposal evidence bundle.

Lineage requirements: must be visible in parent, promotion, rejection,
and rollback lineage.

### replay_id

Purpose: canonical replay identity for the evidence event.

Immutability rules: cannot be reused, reassigned, or edited.

Replay requirements: deterministic and unique within governance
lineage.

Validation requirements: must match the replay identity model.

Lineage requirements: must append to lineage without rewriting prior
replay identities.

### lineage_reference

Purpose: links evidence to prior governance ancestry.

Immutability rules: immutable pointer to predecessor lineage.

Replay requirements: predecessor must remain replay-visible.

Validation requirements: must verify parent/child continuity.

Lineage requirements: append-only and never silently rewritten.

### approval_reference

Purpose: records explicit approval evidence when required.

Immutability rules: cannot be inferred or replaced by advisory output.

Replay requirements: approval evidence must be replay-visible.

Validation requirements: required for mutation classes that require
approval.

Lineage requirements: approval lineage must remain traceable.

### rollback_reference

Purpose: links evidence to rollback plan or rollback event.

Immutability rules: immutable once recorded.

Replay requirements: rollback evidence must be reproducible.

Validation requirements: required for promotable mutation evidence.

Lineage requirements: rollback lineage must append, not erase.

### promotion_reference

Purpose: links evidence to promotion decision evidence.

Immutability rules: cannot be created by replay verification alone.

Replay requirements: promotion evidence must be deterministic.

Validation requirements: required before any promoted status.

Lineage requirements: promotion lineage must remain visible.

### evidence_bundle_hash

Purpose: canonical hash of all evidence inputs.

Immutability rules: immutable after evidence bundle creation.

Replay requirements: replay must reproduce the same hash.

Validation requirements: must be a SHA-256 digest over canonical
serialization.

Lineage requirements: must be referenced by descendants.

### deterministic_hash

Purpose: canonical event hash for replay validation.

Immutability rules: cannot be regenerated with non-deterministic input.

Replay requirements: replay must reproduce the exact value.

Validation requirements: must be computed from canonical field order and
stable serialization.

Lineage requirements: successor evidence references prior deterministic
hashes where applicable.

### certification_status

Purpose: records certification state for governance evidence.

Immutability rules: status events append; prior status is not rewritten.

Replay requirements: certification evidence must be replay-visible.

Validation requirements: must use deterministic allowed status values.

Lineage requirements: certification transitions must be traceable.

### mutation_class

Purpose: classifies governance mutation risk.

Immutability rules: classification changes require new evidence.

Replay requirements: classification must be reproducible.

Validation requirements: must be one of COSMETIC, PARAMETRIC,
STRUCTURAL, CONSTITUTIONAL, or NOT_APPLICABLE.

Lineage requirements: class must be preserved through promotion and
rollback lineage.

### quarantine_status

Purpose: records unsafe, invalid, or uncertain proposal handling.

Immutability rules: quarantine decisions append and cannot be hidden.

Replay requirements: quarantine cause must be replay-visible.

Validation requirements: uncertainty must resolve to quarantined or
blocked status.

Lineage requirements: quarantine lineage remains visible even after
rejection.

### timestamp_reference

Purpose: provides deterministic temporal reference without making
evidence dependent on wall-clock non-determinism.

Immutability rules: immutable after evidence creation.

Replay requirements: must replay as the same reference value.

Validation requirements: must be explicit and deterministic.

Lineage requirements: preserved in the evidence event.

### constitutional_scope

Purpose: identifies affected constitutional domain and protected layer.

Immutability rules: scope changes require new evidence.

Replay requirements: scope classification must be reproducible.

Validation requirements: protected-layer scope must trigger required
approval and quarantine rules.

Lineage requirements: scope remains visible across descendants.

## Deterministic Governance Requirements

Evidence MUST use canonical field ordering, deterministic hashing,
replay-safe serialization, append-only evidence semantics, and
replay-safe validation.

Explicitly prohibited:

- mutable replay evidence;
- non-deterministic replay manifests;
- silent evidence modification;
- unverifiable lineage mutation.

## Architectural Status

This phase does NOT introduce runtime replay engines, governance
mutation, replay-triggered authority, autonomous replay interpretation,
or adaptive replay execution.

This is a constitutional replay evidence foundation only.
