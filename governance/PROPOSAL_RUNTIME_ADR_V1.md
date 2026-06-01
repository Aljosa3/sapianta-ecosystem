# Proposal Runtime ADR V1

Status: accepted with gaps.

## Context

AiGOL has a certified conversational runtime, a resolution strategy foundation, and a proposal lifecycle foundation.

The missing architectural piece is a minimal runtime representation for proposals that can be created from conversation and resolution evidence while remaining replay-safe and non-authoritative.

## Decision

Adopt `PROPOSAL_RUNTIME_ARTIFACT_V1` as the minimal runtime representation of a proposal.

Required fields:

```text
proposal_id
proposal_type
proposal_source
proposal_text
created_at
created_by
status
replay_reference
source_prompt_id
source_conversation_id optional
source_strategy_id optional
source_provider_event_id optional
artifact_hash
```

Final foundation status:

```text
PROPOSAL_RUNTIME_FOUNDATION_STATUS = READY_WITH_GAPS
```

## Rationale

The model is intentionally small. It records proposal identity, source, text, creator, status, replay lineage, and artifact hash.

This is enough to bridge conversational and resolution-strategy evidence into Proposal Lifecycle without implementing execution, approval, worker dispatch, or provider authority.

## Accepted Runtime State

The foundation runtime creates only:

```text
CREATED
```

Other lifecycle-compatible states are recognized but require separate implementation and certification:

```text
INSPECTED
APPROVED
REJECTED
EXPIRED
EXECUTED
```

## Rejected Alternatives

Provider-created proposal authority is rejected because provider output is proposal evidence only.

Direct conversation-to-execution is rejected because Proposal Lifecycle and governed execution request handling must mediate future execution.

Implicit proposal creation without replay evidence is rejected because proposal history must be reconstructable.

Proposal runtime approval is rejected because approval belongs to the lifecycle/human approval boundary, not creation.

## Consequences

Future implementation must:

- create append-only proposal creation evidence;
- preserve `created_by = AIGOL`;
- reject provider-originated authority;
- preserve replay references and artifact hashes;
- keep execution request derivation out of the runtime foundation;
- separately certify inspection, approval, expiration, and execution transitions.

This ADR does not implement runtime behavior.
