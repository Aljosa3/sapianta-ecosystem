# AIGOL_HUMAN_APPROVAL_MODEL_V1

## Status

Human approval model.

## Approval Artifact

Required artifact:

```text
HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1
```

Future decision artifact:

```text
HUMAN_APPROVAL_DECISION_ARTIFACT_V1
```

## Approval Request Fields

`HUMAN_APPROVAL_REQUIRED_ARTIFACT_V1` must include:

- `artifact_type`;
- `approval_request_id`;
- `canonical_chain_id`;
- `approval_reason`;
- `risk_category`;
- `domain_id`;
- `worker_family_id`;
- `milestone_type`;
- `proposal_reference`;
- `proposal_hash`;
- `context_reference`;
- `context_hash`;
- `validation_status`;
- `resume_candidate_stage`;
- `created_at`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Approval Decision Fields

`HUMAN_APPROVAL_DECISION_ARTIFACT_V1` must include:

- `artifact_type`;
- `approval_decision_id`;
- `approval_request_reference`;
- `approval_request_hash`;
- `canonical_chain_id`;
- `decision`;
- `decision_reason_hash`;
- `approved_resume_stage`;
- `human_authority_confirmed`;
- `created_at`;
- `replay_reference`;
- `replay_visible`;
- `artifact_hash`.

## Allowed Decisions

Allowed approval decisions:

- `APPROVED`;
- `REJECTED`;
- `CLARIFICATION_REQUIRED`;
- `CANCELLED`;
- `FAILED_CLOSED`.

## Approval Boundary

Approval authorizes only the next governed continuation stage named in the approval request.

Approval does not authorize:

- execution;
- dispatch;
- worker invocation;
- provider authority;
- governance mutation;
- replay mutation;
- broker integration;
- exchange integration;
- order placement;
- live trading.

## High-Risk Domains

Approval is mandatory for:

- trading;
- healthcare;
- legal;
- critical infrastructure;
- public services.

High-risk approval must be explicit, replay-visible, and hash-linked.

## Approval Outcome Classes

Allowed outcomes:

- `APPROVAL_RECORDED`;
- `APPROVAL_REJECTED`;
- `CLARIFICATION_REQUIRED`;
- `CANCELLED`;
- `FAILED_CLOSED`.

