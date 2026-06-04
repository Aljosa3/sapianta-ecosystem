# AIGOL_PRE_OCS_OPERATOR_EXPERIENCE_REUSE_PLAN_V1

## Status

Review-only reuse plan.

## Reusable Components

### Approval Packet

Reuse `approval_resume_packet` from
`conversation_to_ppp_handoff_execution`. It already preserves context,
registry, provider-policy, proposal, validation, and approval request evidence
with hashes suitable for resume validation.

### Approval Resume Validation

Reuse `implementation_approval_resume` lineage checks for chain id, scope,
proposal hash, request hash, expiration, and replay packet integrity.

### Improvement Approval Decision Shape

Reuse the decision model from `improvement_approval_runtime` as the pattern for
explicit `APPROVED` and `REJECTED` outcomes. Do not reuse its artifact directly
for implementation approval unless lineage fields are specialized for the
conversation-to-implementation packet.

### Chain Inspection Runtime

Reuse `chain_inspection` and `unified_replay_reconstruction_runtime` for
operator inspection. Keep source replay read-only and persist inspection reports
as separate evidence.

### Domain Bundle Registry

Reuse `DOMAIN_BUNDLE_REGISTRY` for supported domain display, registry hash
continuity, and unknown-domain feedback.

## Reuse Boundaries

Reusable components must not gain:

- autonomous approval;
- provider approval authority;
- worker approval authority;
- execution or dispatch authority;
- hidden replay mutation;
- OCS activation authority.

## Recommended Reuse Pattern

1. Add a pending approval inspection command that reads the existing
   `approval_resume_packet`.
2. Add explicit human decision artifacts for approve, reject, and request
   modification.
3. Route only approved artifacts into the existing approval resume path.
4. Route rejected and modification-requested artifacts into terminal
   replay-visible outcomes with no implementation handoff.
5. Add registry-backed supported-domain summaries to unknown-domain failure
   output.
