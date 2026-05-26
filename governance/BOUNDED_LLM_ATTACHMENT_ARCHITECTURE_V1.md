# BOUNDED_LLM_ATTACHMENT_ARCHITECTURE_V1

## Scope

This milestone implements the first bounded cognition attachment architecture for AiGOL.

The architecture defines proposal-only cognition artifacts and replay-visible cognition lineage. It does not execute providers, authorize execution, attach contracts, mutate runtime state, or bypass governance gates.

It exposes:

- `create_bounded_cognition_proposal(...)`
- `reconstruct_cognition_lineage(...)`

## Proposal Evidence

Proposal evidence contains only:

- `proposal_id`
- `proposal_type`
- `proposal_summary`
- `requested_capabilities`
- `proposed_contract_reference`
- `created_at`
- `evidence_hash`

Allowed proposal types are:

- `CONTRACT_PROPOSAL`
- `ROUTING_PROPOSAL`
- `GOVERNANCE_QUERY`

## Guarantees

- Bounded cognition attachment only.
- No execution authority introduced.
- No autonomous cognition introduced.
- Replay-visible cognition lineage.
- Deterministic cognition boundary validation.
- Governance authority separation preserved.
- Proposal to contract interaction remains reference-only.

## Non-Goals

- Real LLM integration.
- Autonomous cognition.
- Semantic planning.
- Orchestration systems.
- Workflow execution.
- Adaptive policy learning.
- Self-modifying governance.
- Runtime autonomy.
- Autonomous provider execution.

## Boundary

Cognition may propose bounded capabilities and reference a proposed contract boundary. Governance remains the only authority for validation, authorization, routing, session attachment, certification, and promotion discipline.

The attachment architecture does not execute, authorize, route, attach, schedule, repair, learn, or mutate runtime state.

## Certification

`BOUNDED_LLM_ATTACHMENT_ARCHITECTURE_V1` certifies bounded proposal-only cognition attachment, replay-visible cognition lineage, deterministic boundary validation, and governance authority separation without introducing execution authority, autonomous cognition, orchestration, semantic planning, runtime autonomy, or real LLM execution.
