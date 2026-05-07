# SAPIANTA Replay Lineage Propagation v1

## Document Role

This document defines replay-safe lineage propagation semantics for governed artifacts across the SAPIANTA ecosystem.

It is documentation-only. It does not implement replay tooling, orchestration, runtime integration, or activation behavior.

## Propagation Flow

Canonical replay lineage propagation:

1. Proposal
2. Validation
3. Replay verification
4. Audit lineage
5. Promotion review
6. Approval lineage
7. Governed promotion

This flow records lineage continuity. It does not activate runtime execution.

## Lineage Continuity

Lineage continuity means each transition preserves:
- source artifact identity
- source repository attribution
- validation evidence
- replay evidence
- audit references
- governance review references
- approval state

Missing lineage continuity blocks governed promotion.

## Replay Identity Preservation

Replay identity preservation requires that replay validation can reconstruct the artifact identity, validation context, replay inputs, replay outputs, and evidence references.

If replay identity cannot be reconstructed deterministically, the artifact must remain unpromoted.

## Deterministic Replay Equivalence

Deterministic replay equivalence means replayed evidence is equivalent to the recorded artifact identity and validation evidence under the same deterministic assumptions.

Equivalence does not imply runtime activation.

## Replay-Safe Ecosystem Propagation

Replay-safe propagation across repositories requires:
- bounded source attribution
- deterministic artifact identity
- approval-gated promotion
- append-only governance memory
- explicit promotion boundaries
- no hidden artifact replacement

## Prohibited Lineage Actions

The ecosystem must prohibit:
- lineage mutation
- hidden lineage rewriting
- implicit artifact replacement
- silent identity substitution
- approval inheritance without identity continuity
- replay evidence reuse without attribution

## Lineage Integrity Failure Rule

- Silent lineage truncation is prohibited.
- Lineage loss is a governance integrity failure.
- Missing lineage blocks governed promotion.
- Lineage must not be silently inferred.
- Lineage recovery requires explicit governance review.

## Future Governed Replay Federation

Future governed replay federation may coordinate replay evidence across multiple repositories.

Current status:
- NOT IMPLEMENTED
- NOT ACTIVE
- NOT AUTHORIZED
