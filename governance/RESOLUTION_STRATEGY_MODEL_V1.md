# Resolution Strategy Model V1

Status: minimal model definition.

## Model Purpose

The Resolution Strategy model defines how AiGOL records which source category should be used for a prompt.

It is a source-of-truth selection artifact.

It is not:

- a response artifact;
- a routing artifact;
- a proposal artifact;
- an execution request;
- a worker task;
- a governance decision.

## Strategy Categories

| Strategy | Description | Provider required |
| --- | --- | --- |
| `SELF_RESOLUTION` | Deterministic AiGOL-local answer or classification | No |
| `CONSTITUTIONAL_MEMORY` | Citation-backed memory evidence | No |
| `GOVERNANCE` | Governance artifact or invariant evidence | No |
| `REPLAY` | Replay-visible operation evidence | No |
| `PROVIDER` | External semantic assistance | Sometimes |
| `WORKER` | Future authorized worker result evidence | No provider requirement by itself |
| `COMBINED` | Multiple strategies with explicit source precedence | Depends on included strategies |

## Minimal Fields

| Field | Required | Meaning |
| --- | --- | --- |
| `strategy_id` | Yes | Stable strategy selection identity |
| `strategy_version` | Yes | Model version |
| `source_prompt_id` | Yes | Human prompt lineage |
| `source_conversation_id` | No | Conversation lineage when present |
| `intent_id` | No | Intent classification lineage when present |
| `candidate_strategies` | Yes | Ordered candidate strategies considered |
| `selected_strategy` | Yes | Selected source category |
| `selection_reason` | Yes | Deterministic reason for selection |
| `source_precedence` | Yes | Order used when multiple sources are available |
| `evidence_refs` | Yes | Replay, governance, memory, provider, or worker references |
| `provider_required` | Yes | Whether provider assistance is required |
| `provider_used` | Yes | Whether provider assistance was used |
| `worker_required` | Yes | Whether worker result evidence is required |
| `proposal_lifecycle_required` | Yes | Whether future proposal lifecycle is required |
| `fail_closed_reason` | No | Reason strategy selection failed closed |
| `created_by` | Yes | Must be `AIGOL` |
| `created_at` | Yes | Creation timestamp |
| `artifact_hash` | Yes | Deterministic artifact hash |

## Selection Statuses

```text
SELECTED
FAILED_CLOSED
DEFERRED_TO_PROPOSAL_LIFECYCLE
REPLAY_RECONSTRUCTED
```

## Source Precedence

When multiple sources can answer, AiGOL should prefer the most direct replay-safe source.

Default precedence:

```text
REPLAY
GOVERNANCE
CONSTITUTIONAL_MEMORY
SELF_RESOLUTION
PROVIDER
WORKER
COMBINED
```

`COMBINED` must explicitly record precedence among included source categories.

## Provider Fields

Provider assistance is valid only when:

- deterministic sources are insufficient;
- provider use is allowed by boundary rules;
- provider output is validated by AiGOL;
- provider output remains non-authoritative;
- replay records the provider request, response, validation, and acceptance or rejection.

## Worker Fields

`WORKER` means a worker result is needed as future evidence.

It does not authorize worker execution.

If worker evidence is required, selection should defer into Proposal Lifecycle and future governed execution request handling.

## Proposal Lifecycle Fields

`proposal_lifecycle_required = true` when:

- the prompt asks AiGOL to do something beyond conversational explanation;
- worker result evidence is needed;
- a future action candidate is detected;
- approval-sensitive capability is requested.

Resolution Strategy may trigger proposal candidacy, but AiGOL alone creates proposal lifecycle state.

## Validity Rules

A strategy selection is invalid if:

- selected strategy is not in the candidate set;
- provider is required for `REPLAY`, `GOVERNANCE`, or authority determination;
- worker execution is implied without proposal lifecycle;
- source evidence references are missing;
- `created_by` is not `AIGOL`;
- provider output is treated as authority;
- replay lineage cannot be reconstructed.

Invalid selections must fail closed.
