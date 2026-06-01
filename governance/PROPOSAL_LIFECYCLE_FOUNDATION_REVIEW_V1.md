# Proposal Lifecycle Foundation Review V1

Status: foundation review.

Final classification:

```text
PROPOSAL_LIFECYCLE_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This review defines the minimal proposal lifecycle architecture needed to bridge:

```text
Conversation
-> Governance
-> Future Worker Execution
```

It does not implement runtime, workers, execution, providers, authorization, governance mutation, or deployment behavior.

## Context

`CONVERSATIONAL_RUNTIME_V1` is now certified as an operational human conversational entry point with gaps.

The current operational flow is:

```text
Human
-> AiGOL
-> Provider optional
-> AiGOL
-> Replay
-> Human
```

The next bounded capability is a proposal lifecycle that can preserve conversational ingress while preparing future governed execution without granting authority to providers.

## 1. What Is A Proposal?

A proposal is a replay-visible, non-authoritative candidate for future governed action.

A proposal may be derived from:

- human conversational intent;
- provider-assisted classification;
- provider-assisted response content;
- AiGOL deterministic normalization;
- prior replay-visible context.

A proposal is not trusted until AiGOL inspects and validates it. A proposal never executes, authorizes, governs, dispatches, or mutates runtime state by itself.

## 2. Proposal Distinctions

| Object | Meaning | Authority |
| --- | --- | --- |
| Conversation response | Human-readable answer returned by AiGOL | No execution authority |
| Proposal | Candidate future action or structured intent | No authority until governed approval |
| Execution request | Governed request derived from approved proposal | May authorize bounded worker execution when valid |
| Worker task | Deterministic work unit executed by worker | Executes only after authorization |
| Governance artifact | Constitutional or evidentiary control artifact | Defines or records governance constraints |

The proposal is the bridge object. It sits after conversation and before execution request creation.

## 3. Required Lifecycle States

The minimal lifecycle requires:

| State | Meaning |
| --- | --- |
| `CREATED` | AiGOL records a candidate proposal artifact |
| `INSPECTED` | AiGOL validates structure, scope, lineage, and boundaries |
| `APPROVED` | Human approval has been explicitly recorded after AiGOL inspection |
| `REJECTED` | AiGOL or human rejects the proposal |
| `EXPIRED` | Proposal can no longer be used for future execution |
| `EXECUTED` | A downstream governed execution request was executed by worker |
| `REPLAY_RECONSTRUCTED` | Replay reconstructs lifecycle history from recorded evidence |

## 4. Actor Transition Authority

| Transition | Actor | Authority Rule |
| --- | --- | --- |
| Conversation evidence to `CREATED` | AiGOL | AiGOL creates proposal artifacts from bounded evidence |
| Provider suggestion to `CREATED` | AiGOL | Provider suggests only; AiGOL creates if valid enough to record |
| `CREATED` to `INSPECTED` | AiGOL | Deterministic inspection only |
| `INSPECTED` to `APPROVED` | Human | Requires explicit human approval |
| `INSPECTED` to `REJECTED` | AiGOL or Human | AiGOL rejects invalid proposals; human may reject valid proposals |
| `CREATED` or `INSPECTED` to `EXPIRED` | AiGOL | Deterministic expiry rule |
| `APPROVED` to execution request candidate | AiGOL | AiGOL may derive a governed execution request |
| Execution request to `EXECUTED` | Worker | Worker executes only authorized bounded work |
| Any recorded history to `REPLAY_RECONSTRUCTED` | Replay | Replay reconstructs; it does not mutate lifecycle truth |

Provider has no lifecycle transition authority.

Worker has no proposal approval authority.

Replay has no proposal mutation authority.

## 5. Human Approval Requirements

Explicit human approval is required for:

- `INSPECTED` to `APPROVED`;
- any future transition from approved proposal into governed execution request creation when policy requires approval evidence;
- any capability that may result in worker execution, external effect, write effect, network effect, or governance-sensitive action.

Human approval is not sufficient by itself. AiGOL governance validation remains required.

## 6. Replay Reconstruction

Replay reconstructs proposal history by reading append-only lifecycle events in deterministic order:

```text
PROPOSAL_CREATED
PROPOSAL_INSPECTED
PROPOSAL_APPROVED
PROPOSAL_REJECTED
PROPOSAL_EXPIRED
PROPOSAL_EXECUTION_REQUEST_DERIVED
PROPOSAL_EXECUTED
```

Replay reconstruction must preserve:

- proposal identity;
- source prompt identity;
- provider contribution identity when present;
- inspection result;
- human approval evidence when present;
- rejection or expiry reason;
- execution request reference when present;
- worker execution reference when present;
- artifact hashes.

Replay reconstruction may emit `REPLAY_RECONSTRUCTED` as a read-only reconstruction status. It must not change the underlying proposal lifecycle.

## 7. Constitutional Preservation

The lifecycle preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Constitutional role | Lifecycle meaning |
| --- | --- |
| LLM proposes | Provider output may contribute proposal evidence only |
| AiGOL governs | AiGOL creates, inspects, validates, rejects, expires, and derives governed requests |
| Worker executes | Worker acts only after approved governed execution request |
| Replay records | Replay records and reconstructs lifecycle evidence |

## 8. Smallest Proposal Model

The smallest proposal model that can support future worker execution is:

```text
proposal_id
proposal_version
source_prompt_id
source_conversation_id
source_provider_event_id optional
created_by = AIGOL
proposal_type
capability_target
proposed_operation
proposed_arguments
constraints
risk_class
state
inspection_result optional
human_approval_id optional
execution_request_id optional
worker_result_id optional
created_at
expires_at optional
replay_refs
artifact_hash
```

This model is intentionally minimal. It supports lineage, inspection, approval, future execution request derivation, and replay reconstruction without granting proposal authority to the provider.

## Foundation Result

The minimal proposal lifecycle foundation is ready as an architectural review artifact.

It remains ready with gaps because runtime implementation, schema enforcement, tests, approval UI, and worker execution integration are not implemented or certified by this review.

```text
PROPOSAL_LIFECYCLE_FOUNDATION_STATUS = READY_WITH_GAPS
```
