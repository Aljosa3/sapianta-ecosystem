# SAPIANTA Replay Lineage Model v1

## Document Role

This document defines replay lineage movement across the SAPIANTA ecosystem.

It is documentation-only. It does not implement replay tooling, artifact promotion, runtime integration, or enforcement.

## Extension References

Governed artifact identity and replay lineage continuity are further specified in:
- `ARCHITECTURE/ARTIFACT_IDENTITY_MODEL_v1.md`
- `ARCHITECTURE/REPLAY_LINEAGE_PROPAGATION_v1.md`
- `ARCHITECTURE/PROMOTION_LINEAGE_CONTINUITY_v1.md`
- `ARCHITECTURE/AUDIT_CONTINUITY_MODEL_v1.md`
- `ARCHITECTURE/GOVERNED_ARTIFACT_INHERITANCE_v1.md`

These references do not implement replay tooling or change activation semantics.

## Lineage Principles

Replay lineage must be:
- deterministic
- append-only where recorded in governance memory
- repository-aware
- artifact-identity aware
- promotion-aware
- activation-gated

Lineage records explain how artifacts moved, why they were accepted, and which authority approved them.

## Lineage Integrity Failure Rule

- Silent lineage truncation is prohibited.
- Lineage loss is a governance integrity failure.
- Missing lineage blocks governed promotion.
- Lineage must not be silently inferred.
- Lineage recovery requires explicit governance review.

## Deterministic Artifact Identity

Future artifact identity should include:
- source repository
- artifact path or contract name
- content hash or deterministic identity
- generation or validation context
- promotion status
- approval lineage
- replay inputs and outputs when applicable

This document defines intent only. It does not create hashing or replay automation.

## Lineage Propagation

Allowed lineage propagation:
- domains expose deterministic contracts and replay artifacts
- runtime consumes approved artifacts and records runtime replay outputs
- factory emits proposal lineage without authority
- governance memory records promotion rationale and approval state
- meta root links cross-repository lineage

Forbidden lineage propagation:
- factory proposals becoming runtime artifacts without approval
- domain experiments becoming production execution without activation lineage
- governance memory executing replay flows
- unapproved artifacts entering runtime lineage as accepted state

## Promotion Lineage

Promotion lineage must record:
- originating repository
- proposed artifact
- validation evidence
- approval rationale
- target authority
- activation status
- related milestone
- related ADR when semantic architecture changes

Promotion lineage does not automatically activate execution.

## Replay-Safe Orchestration

Future orchestration may coordinate replay across repositories only through approved contracts and deterministic artifact identities.

Replay-safe orchestration remains future work and requires separate approval before implementation.

## Governance Memory

Governance memory remains append-only for:
- milestones
- ADRs
- promotion decisions
- domain state investigations
- replay lineage summaries

Canonical state documents may be updated to reflect current authority, but historical lineage must not be deleted.
