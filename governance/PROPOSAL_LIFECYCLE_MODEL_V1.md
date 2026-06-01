# Proposal Lifecycle Model V1

Status: minimal model definition.

## Model Purpose

The proposal model defines the smallest replay-safe object that can bridge conversation into future governed execution.

A proposal is:

- replay-visible;
- non-authoritative;
- inspectable by AiGOL;
- eligible for explicit human approval;
- derivable into a governed execution request only after required validation.

## Proposal Is Not

A proposal is not:

- a conversation response;
- an execution request;
- a worker task;
- a governance artifact;
- provider authority;
- human approval by itself;
- execution authority.

## Minimal Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `proposal_id` | Yes | Stable proposal identity |
| `proposal_version` | Yes | Model version |
| `source_prompt_id` | Yes | Human prompt lineage |
| `source_conversation_id` | Yes | Conversation lineage |
| `source_provider_event_id` | No | Provider contribution lineage |
| `created_by` | Yes | Must be `AIGOL` |
| `proposal_type` | Yes | Proposal category |
| `capability_target` | Yes | Bounded future capability target |
| `proposed_operation` | Yes | Requested operation semantics |
| `proposed_arguments` | Yes | Structured operation arguments |
| `constraints` | Yes | Boundary, scope, and safety constraints |
| `risk_class` | Yes | Minimal risk classification |
| `state` | Yes | Current lifecycle state |
| `inspection_result` | No | AiGOL inspection evidence |
| `human_approval_id` | No | Explicit approval reference |
| `execution_request_id` | No | Future governed execution request reference |
| `worker_result_id` | No | Future worker result reference |
| `created_at` | Yes | Creation timestamp |
| `expires_at` | No | Deterministic expiry timestamp or condition |
| `replay_refs` | Yes | Append-only replay references |
| `artifact_hash` | Yes | Deterministic artifact hash |

## Required States

```text
CREATED
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
REPLAY_RECONSTRUCTED
```

## Proposal Type Minimum Set

The foundation model requires only:

```text
CAPABILITY_PROPOSAL
```

Future model versions may add more proposal types only through governed review.

## Risk Class Minimum Set

The foundation model requires:

```text
READ_ONLY
WRITE_OR_MUTATION
EXTERNAL_EFFECT
GOVERNANCE_SENSITIVE
UNKNOWN
```

`UNKNOWN` must fail closed before approval or execution request derivation.

## State Semantics

`CREATED` means AiGOL recorded a candidate proposal. It does not mean the proposal is valid.

`INSPECTED` means AiGOL inspected structure, capability target, arguments, lineage, constraints, and authority boundaries.

`APPROVED` means explicit human approval was recorded after inspection. Approval does not bypass AiGOL governance.

`REJECTED` means AiGOL or human blocked the proposal.

`EXPIRED` means proposal use is no longer allowed.

`EXECUTED` means a downstream governed execution request derived from the approved proposal was executed by a worker.

`REPLAY_RECONSTRUCTED` means replay reconstructed lifecycle history without mutating lifecycle state.

## Minimal Validity Rules

A proposal is invalid if:

- `created_by` is not `AIGOL`;
- source prompt lineage is missing;
- conversation lineage is missing;
- capability target is missing or unsupported;
- proposed arguments are malformed;
- risk class is `UNKNOWN`;
- provider text claims authority;
- human approval is missing for approval-required transitions;
- replay references are missing;
- artifact hash cannot be reconstructed.

Invalid proposals must become `REJECTED` or remain unusable.

## Future Worker Compatibility

The model supports future worker execution by preserving:

- bounded capability target;
- proposed operation;
- proposed arguments;
- constraints;
- approval evidence;
- execution request reference;
- worker result reference;
- replay lineage.

It does not itself execute.
