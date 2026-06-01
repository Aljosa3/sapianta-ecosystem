# Proposal Approval Model V1

Status: minimal approval model.

## Model Purpose

The Proposal Approval Model defines how explicit human approval evidence is represented before any future execution path may proceed.

Approval is evidence.

Approval is not execution.

Approval is not provider authority.

Approval is not worker authority.

## Approval Artifact

The minimal approval artifact is:

```text
PROPOSAL_APPROVAL_ARTIFACT_V1
```

## Required Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `approval_id` | Yes | Stable approval evidence identity |
| `proposal_id` | Yes | Proposal being approved, rejected, or expired |
| `proposal_artifact_hash` | Yes | Hash of proposal artifact under review |
| `inspection_artifact_ref` | Yes | AiGOL inspection evidence reference |
| `inspection_artifact_hash` | Yes | Hash of inspection artifact |
| `human_decision` | Yes | Human decision value |
| `approval_status` | Yes | Approval state |
| `approval_reason` | Yes | Human-readable reason or operator note |
| `operator_label` | Yes | Human operator label |
| `created_at` | Yes | Approval artifact creation timestamp |
| `replay_reference` | Yes | Replay lineage reference |
| `non_execution_flags` | Yes | Explicit proof approval did not execute |
| `artifact_hash` | Yes | Deterministic approval artifact hash |

## Approval States

```text
PENDING_APPROVAL
APPROVED
REJECTED
EXPIRED
```

## Human Decision Values

```text
APPROVE
REJECT
EXPIRE
```

`PENDING_APPROVAL` means no final human decision has been recorded.

## Non-Execution Flags

Every approval artifact must preserve:

```text
execution_performed = false
worker_dispatched = false
provider_dispatched = false
execution_request_created = false
autonomous_continuation_performed = false
governance_mutation_performed = false
```

## Approval Preconditions

Approval is valid only if:

- proposal exists;
- proposal status is `INSPECTED`;
- inspection artifact exists;
- proposal hash matches;
- inspection hash matches;
- proposal is not expired;
- proposal is not rejected;
- proposal is not executed;
- human operator decision is explicit;
- replay reference exists.

## Invalid Approval Conditions

Approval is invalid if:

- provider made the decision;
- worker made the decision;
- replay inferred the decision;
- proposal is only `CREATED` and not inspected;
- inspection failed;
- artifact hash mismatches;
- execution already occurred;
- approval claims execution authority;
- approval omits non-execution flags.

Invalid approval must fail closed.

## Lifecycle Relationship

Approval model state maps to proposal lifecycle state as:

| Approval state | Lifecycle effect |
| --- | --- |
| `PENDING_APPROVAL` | Proposal remains `INSPECTED` |
| `APPROVED` | Proposal may transition `INSPECTED -> APPROVED` |
| `REJECTED` | Proposal may transition `INSPECTED -> REJECTED` |
| `EXPIRED` | Proposal may transition `INSPECTED -> EXPIRED` |

Approval does not create execution requests.
