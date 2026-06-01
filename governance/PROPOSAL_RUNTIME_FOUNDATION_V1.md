# Proposal Runtime Foundation V1

Status: foundation review.

Final classification:

```text
PROPOSAL_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Scope

This artifact defines the minimal proposal runtime architecture needed to represent proposals as replay-visible runtime artifacts.

It does not implement runtime code, workers, execution, routing, provider behavior, governance mutation, approval UI, or deployment behavior.

## Context

AiGOL now has:

- certified conversational runtime;
- resolution strategy foundation;
- proposal lifecycle foundation.

The next boundary is a minimal runtime representation that can record a proposal created from conversation and strategy evidence without granting authority to providers or creating execution.

## 1. How A Proposal Is Created

A proposal is created only by AiGOL.

Proposal creation may be triggered when:

- conversational runtime detects a future action candidate;
- resolution strategy determines `proposal_lifecycle_required = true`;
- provider output contributes bounded proposal evidence;
- replay-visible human prompt evidence describes a requested future action;
- deterministic AiGOL normalization produces a bounded proposal candidate.

Provider output may contribute proposal evidence, but provider output may not create authoritative proposal state.

Human prompt text may request action, but human prompt text may not create execution authority.

## 2. Runtime Artifact

The minimal runtime artifact is:

```text
PROPOSAL_RUNTIME_ARTIFACT_V1
```

It represents a candidate future governed action.

It is:

- replay-visible;
- non-authoritative;
- created by AiGOL;
- eligible for later inspection;
- not executable by itself.

## 3. Mandatory Fields

The smallest runtime artifact requires:

```text
proposal_id
proposal_type
proposal_source
proposal_text
created_at
created_by
status
replay_reference
```

To preserve lifecycle compatibility, the foundation also requires:

```text
source_prompt_id
source_conversation_id optional
source_strategy_id optional
source_provider_event_id optional
artifact_hash
```

## 4. Replay Visibility

Proposal creation remains replay-visible by recording:

```text
PROPOSAL_RUNTIME_CREATED
PROPOSAL_RUNTIME_RETURNED
```

The creation event must include:

- source prompt reference;
- source conversation reference when present;
- resolution strategy reference when present;
- provider contribution reference when present;
- proposal artifact hash;
- non-authority status;
- initial lifecycle status.

Replay reconstruction must be able to reconstruct proposal identity, source evidence, status, and artifact hash without invoking a provider, worker, or runtime mutation.

## 5. Integration

### Conversational Runtime

Conversational Runtime may surface a future action candidate.

It does not approve, execute, or dispatch the proposal.

### Resolution Strategy

Resolution Strategy may determine that Proposal Lifecycle is required.

It does not create approved proposal state or execution requests.

### Replay

Replay records proposal creation evidence and reconstructs proposal history.

Replay does not mutate proposal status.

## 6. Runtime-Valid States

The runtime-valid proposal states are:

```text
CREATED
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
```

The runtime foundation records `CREATED` only.

Other states are lifecycle-compatible future states and require separate implementation or certification.

## 7. Illegal Transition Prevention

Illegal transitions are prevented by:

- allowing AiGOL only to create runtime proposal artifacts;
- requiring explicit transition tables before state mutation;
- requiring replay lineage for every transition;
- rejecting provider-originated state changes;
- rejecting worker-originated approval or scope changes;
- rejecting execution-related states without governed execution request references;
- failing closed when status, actor, lineage, or artifact hash cannot be validated.

## 8. Constitutional Preservation

Proposal Runtime preserves:

```text
LLM proposes
AiGOL governs
Worker executes
Replay records
```

Mapping:

| Role | Runtime meaning |
| --- | --- |
| LLM proposes | Provider output may contribute proposal evidence only |
| AiGOL governs | AiGOL creates and validates proposal runtime artifacts |
| Worker executes | Worker execution is absent from this foundation |
| Replay records | Replay records proposal creation and reconstruction evidence |

## Foundation Result

The minimal proposal runtime foundation is ready as a design artifact.

It remains ready with gaps because no runtime code, schema enforcement, transition implementation, approval surface, execution request derivation, worker integration, or tests are introduced by this review.

```text
PROPOSAL_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```
