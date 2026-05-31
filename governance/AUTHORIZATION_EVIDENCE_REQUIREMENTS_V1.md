# AUTHORIZATION_EVIDENCE_REQUIREMENTS_V1

## Status

Certified authorization evidence requirements.

## Minimum Admissible Evidence

An authorization record must include:

- authorization_id
- proposal_reference
- proposal_lineage
- governance_review_reference
- authorization_identity
- authorization_timestamp
- authorization_status
- worker_target
- worker_identity
- execution_scope
- target_capability
- capability_binding
- replay_reference
- authorization_hash

## Required Proofs

Authorization must prove:

- proposal was reviewed
- governance boundary was applied
- worker target is explicit
- execution scope is bounded
- capability is authorized
- replay lineage is intact
- no hidden continuation exists
- no authority escalation exists

## Forbidden Evidence Gaps

Authorization is not admissible if any of the following are missing or invalid:

- proposal lineage
- governance review
- authorization record
- worker target
- execution scope
- authorization timestamp
- authorization identity
- replay reference

## Certification

The minimum admissible authorization evidence is sufficient only if it remains
replay-visible, deterministic, bounded, and fail-closed.
