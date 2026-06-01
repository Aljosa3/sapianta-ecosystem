# Proposal Runtime Model V1

Status: minimal runtime model.

## Model Purpose

The Proposal Runtime Model defines the smallest replay-safe runtime artifact for representing a proposal candidate.

It is intended to bridge:

```text
Conversational Runtime
-> Resolution Strategy
-> Proposal Lifecycle
-> Future Governed Execution
```

It does not implement runtime behavior.

## Artifact Identity

The runtime artifact is:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

It represents a candidate future governed action created by AiGOL.

## Required Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `proposal_id` | Yes | Stable proposal identity |
| `proposal_type` | Yes | Runtime proposal category |
| `proposal_source` | Yes | Source category that produced the proposal candidate |
| `proposal_text` | Yes | Human-readable bounded proposal summary |
| `created_at` | Yes | Creation timestamp |
| `created_by` | Yes | Must be `AIGOL` |
| `status` | Yes | Runtime lifecycle status |
| `replay_reference` | Yes | Primary replay lineage reference |
| `source_prompt_id` | Yes | Human prompt lineage |
| `source_conversation_id` | No | Conversation lineage when present |
| `source_strategy_id` | No | Resolution strategy lineage when present |
| `source_provider_event_id` | No | Provider contribution lineage when present |
| `artifact_hash` | Yes | Deterministic hash of the proposal artifact |

## Optional Future Fields

Future versions may add:

- `capability_target`;
- `proposed_operation`;
- `proposed_arguments`;
- `constraints`;
- `risk_class`;
- `inspection_result`;
- `human_approval_id`;
- `execution_request_id`;
- `worker_result_id`;
- `expires_at`.

These are lifecycle and execution-compatibility fields. They are not required for the minimal runtime representation.

## Proposal Sources

Valid `proposal_source` values:

```text
CONVERSATION
RESOLUTION_STRATEGY
PROVIDER_EVIDENCE
REPLAY_EVIDENCE
GOVERNANCE_EVIDENCE
HUMAN_PROMPT
COMBINED
```

`PROVIDER_EVIDENCE` does not mean provider-created authority. It means AiGOL created a proposal artifact from bounded provider contribution evidence.

## Proposal Types

The minimum valid `proposal_type` is:

```text
CAPABILITY_PROPOSAL
```

Additional proposal types require separate governed review.

## Creation Rule

`created_by` must be:

```text
AIGOL
```

Any proposal artifact claiming creation by provider, worker, replay, or external actor must fail closed.

## Runtime Status

The minimal runtime may create only:

```text
CREATED
```

The model recognizes lifecycle-compatible statuses:

```text
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
```

Those require lifecycle transition evidence and are not created implicitly by the proposal runtime foundation.

## Validity Rules

A proposal runtime artifact is invalid if:

- `proposal_id` is missing;
- `proposal_type` is unsupported;
- `proposal_source` is unsupported;
- `proposal_text` is empty;
- `created_by` is not `AIGOL`;
- `status` is not runtime-valid;
- `replay_reference` is missing;
- `source_prompt_id` is missing;
- `artifact_hash` cannot be reconstructed;
- provider authority is implied;
- execution authority is implied.

Invalid artifacts must fail closed and must not become execution requests.
