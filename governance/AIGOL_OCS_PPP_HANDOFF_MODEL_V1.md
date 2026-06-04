# AIGOL_OCS_PPP_HANDOFF_MODEL_V1

## Status

Contract model.

## Purpose

This model defines how OCS may hand bounded work to PPP.

PPP remains the proposal pipeline. OCS does not replace PPP and does not gain
PPP authority.

## Handoff Position

Canonical handoff:

```text
OCS Context Assembly
-> OCS Proposal-Only Handoff Packet
-> Governed Task Intake / Resource Selection
-> PPP
-> Proposal Production
-> Proposal Validation
-> Clarification / Approval
-> Implementation Handoff where authorized
```

## Handoff Packet

A future handoff artifact should use:

```text
OCS_PPP_HANDOFF_PACKET_V1
```

Required fields:

- `artifact_type`;
- `contract_version`;
- `handoff_id`;
- `source_context_id`;
- `source_context_hash`;
- `operator_request_reference`;
- `target_domain`;
- `target_registry_reference`;
- `proposed_task_class`;
- `proposed_outputs`;
- `validation_scope`;
- `provider_necessity_classification`;
- `resource_selection_requirements`;
- `approval_policy`;
- `known_gaps`;
- `authority_flags`;
- `handoff_status`.

## Allowed Handoff Statuses

Allowed statuses:

- `PPP_HANDOFF_CANDIDATE_CREATED`;
- `PPP_HANDOFF_REQUIRES_CLARIFICATION`;
- `PPP_HANDOFF_BLOCKED`;
- `PPP_HANDOFF_FAILED_CLOSED`.

No handoff status may imply execution authorization.

## PPP Boundary

OCS may provide PPP with:

- normalized context reference;
- context hash;
- target domain reference;
- proposed task class;
- proposed output list;
- validation scope;
- provider necessity classification reference;
- known gaps;
- clarification requirements.

OCS may not provide PPP with:

- execution authorization;
- worker invocation authority;
- hidden provider instructions;
- bypassed Resource Selection;
- unvalidated domain selection;
- governance mutation request;
- replay mutation request.

## Human Authority

If the PPP path reaches an approval-required state, the certified human decision
runtime remains authoritative.

OCS cannot convert a PPP handoff into approval.

## Replay Visibility

The handoff must be reconstructable from:

- context assembly artifact;
- context hash;
- handoff packet;
- registry resolution artifacts;
- provider necessity policy artifacts;
- PPP validation artifacts;
- human decision artifacts where reached.

Replay must be able to show that OCS produced a proposal-only packet, not an
authorization-bearing command.
