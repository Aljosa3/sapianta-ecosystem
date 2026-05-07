# SAPIANTA Runtime Acceptance Gate v1

## Document Role

This document defines future runtime acceptance requirements for artifacts entering `sapianta_system`.

It is documentation-only. It does not implement acceptance tooling, runtime integration, enforcement, or activation behavior.

## Identity And Lineage References

Runtime acceptance concepts depend on governed artifact identity and lineage continuity as documented in:
- `ARCHITECTURE/ARTIFACT_IDENTITY_MODEL_v1.md`
- `ARCHITECTURE/REPLAY_LINEAGE_PROPAGATION_v1.md`
- `ARCHITECTURE/PROMOTION_LINEAGE_CONTINUITY_v1.md`
- `ARCHITECTURE/AUDIT_CONTINUITY_MODEL_v1.md`
- `ARCHITECTURE/GOVERNED_ARTIFACT_INHERITANCE_v1.md`

These references do not implement runtime acceptance.

## Acceptance Principle

`sapianta_system` may accept artifacts only through explicit, deterministic, governance-aware acceptance gates.

Existence of a domain repository, factory proposal, milestone, or ADR does not imply runtime acceptance.

## Lineage Integrity Failure Rule

- Silent lineage truncation is prohibited.
- Lineage loss is a governance integrity failure.
- Missing lineage blocks governed promotion.
- Lineage must not be silently inferred.
- Lineage recovery requires explicit governance review.

## Acceptance Requirements

Before runtime acceptance, an artifact must have:
- deterministic tests passing
- replay validation passing
- source lineage
- artifact identity continuity
- contract validation
- policy validation where applicable
- governance review
- approval evidence
- repository authority confirmation

## Replay-Safe Promotion

Replay-safe promotion requires:
- stable artifact identity
- deterministic validation evidence
- reproducible replay evidence
- explicit source repository attribution
- approval lineage
- bounded target integration scope

Promotion does not automatically imply runtime execution unless activation is explicitly approved.

## Audit Lineage Preservation

Acceptance lineage must preserve:
- source repository
- proposal origin
- validation evidence
- replay evidence
- review decision
- approval scope
- target runtime boundary
- rollback or rejection decision when applicable

## Rejection Semantics

Artifacts must be rejected when:
- deterministic validation fails
- replay validation fails
- lineage is missing
- artifact identity is ambiguous
- contract validation fails
- policy validation fails where applicable
- authority is unclear
- approval evidence is absent

Rejected artifacts may remain as historical lineage but must not enter accepted runtime state.

## Rollback Semantics

Future rollback semantics must preserve:
- prior accepted artifact identity
- rejected or revoked artifact identity
- reason for rollback
- replay evidence
- governance review record
- restored runtime boundary

Rollback remains future design. This document does not implement it.

## Runtime Authority

Runtime acceptance belongs to `sapianta_system` under explicit governance-aware rules.

Meta-root memory, factory output, and domain repositories cannot directly mutate runtime acceptance state.
