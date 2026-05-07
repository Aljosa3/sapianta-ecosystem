# SAPIANTA Promotion Lineage Continuity v1

## Document Role

This document defines governed promotion lineage continuity for artifacts moving across SAPIANTA repositories.

It is documentation-only. It does not implement promotion automation, runtime acceptance, rollback tooling, or activation behavior.

## Promotion Continuity Principle

Promotion MUST preserve:
- source artifact identity
- originating repository
- validation evidence
- replay evidence
- governance review evidence
- approval scope
- promotion rationale

Promotion without continuity is invalid as governed architecture.

## Lineage Integrity Failure Rule

- Silent lineage truncation is prohibited.
- Lineage loss is a governance integrity failure.
- Missing lineage blocks governed promotion.
- Lineage must not be silently inferred.
- Lineage recovery requires explicit governance review.

## Evidence Continuity

Promotion evidence continuity means validation, replay, audit, and review evidence remain linked to the exact artifact identity being promoted.

Evidence cannot be reused for a changed artifact unless the changed artifact receives new identity and new review.

## Approval Inheritance

Approval may be inherited only when:
- artifact identity is stable
- validation evidence is preserved
- replay evidence is preserved
- approval scope remains unchanged
- target boundary remains within approved authority

Approval inheritance must not imply runtime activation unless activation was explicitly included in approval lineage.

## Validation Inheritance

Validation evidence may be inherited by a promoted artifact only when deterministic identity continuity is preserved.

If the artifact changes, validation inheritance must be reviewed or regenerated.

## Replay Inheritance

Replay evidence may be inherited only when deterministic replay identity remains equivalent.

Replay inheritance does not create execution authority.

## Rejection Lineage

Rejected artifacts remain part of governance and audit lineage.

Rejection lineage should preserve:
- rejected artifact identity
- reason for rejection
- failed validation or replay evidence
- rejecting authority
- future reconsideration constraints when applicable

## Rollback Lineage

Rollback lineage should preserve:
- artifact identity being rolled back
- previous accepted identity
- rollback reason
- replay evidence
- governance review record
- restored authority boundary

Rollback semantics remain future design.

## Revocation Lineage

Revocation lineage should preserve:
- revoked artifact identity
- revocation reason
- revocation authority
- affected approvals
- affected promotions
- replacement status when applicable

Revocation does not delete historical lineage.
