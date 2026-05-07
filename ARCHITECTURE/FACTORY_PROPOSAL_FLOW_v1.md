# SAPIANTA Factory Proposal Flow v1

## Document Role

This document defines factory proposal flow semantics for `sapianta_factory`.

It is documentation-only. It does not activate the factory, implement proposal automation, or grant mutation authority.

## Factory May

The factory may:
- generate proposals
- generate artifacts
- generate tests
- simulate architecture ideas
- propose bounded improvements
- produce validation evidence
- produce implementation candidates for review

All factory output is non-authoritative.

## Factory Must Not

The factory must not:
- mutate runtime directly
- mutate governance memory directly
- self-promote
- activate domains
- modify the policy engine
- modify the Decision Spine
- deploy changes
- execute production logic
- create background execution loops
- bypass repository authority rules

## Proposal Flow

1. Proposal request or domain concept is defined.
2. Factory produces candidate artifacts in sandbox isolation.
3. Candidate artifacts receive deterministic identity when appropriate.
4. Candidate artifacts are reviewed outside the factory.
5. Validation evidence is linked to the proposal.
6. Governance review determines whether promotion is allowed.
7. Approved artifacts may move to the appropriate authority root through human-reviewed workflow.

## Promotion Boundary

Factory output cannot promote itself.

Promotion requires:
- human review
- source attribution
- deterministic artifact identity
- validation evidence
- replay-safety review
- repository authority check
- governance lineage update
- ADR update if semantic architecture changes

## Factory Status

The factory remains:
- sandbox-only
- proposal-only
- governance-dependent
- non-runtime
- non-governance-authoritative

No factory activation is introduced by this document.
