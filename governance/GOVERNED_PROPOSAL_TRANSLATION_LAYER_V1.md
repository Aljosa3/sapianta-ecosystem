# GOVERNED_PROPOSAL_TRANSLATION_LAYER_V1

## Scope

This milestone implements deterministic proposal translation for AiGOL.

The translation layer accepts bounded cognition proposals and emits governed execution contract candidates. It does not create governed execution contracts, authorize contracts, route contracts, attach contracts, mutate runtime state, or execute providers.

It exposes:

- `translate_bounded_proposal(...)`
- `reconstruct_translation_lineage(...)`

## Translation Evidence

Translation evidence contains only:

- `translation_id`
- `proposal_id`
- `translated_contract_candidate`
- `translation_status`
- `translation_reason`
- `created_at`
- `evidence_hash`

Allowed statuses are:

- `TRANSLATED`
- `REJECTED`

## Guarantees

- Deterministic proposal translation only.
- No execution authority introduced.
- No orchestration introduced.
- Replay-visible translation evidence.
- Governance authority separation preserved.
- No autonomous cognition introduced.
- Contract candidates remain governance-constrained.

## Non-Goals

- Real LLM execution.
- Autonomous cognition.
- Orchestration systems.
- Semantic planning.
- Workflow execution.
- Provider execution.
- Adaptive policy learning.
- Runtime autonomy.
- Self-modifying governance.

## Boundary

The translation layer converts proposal evidence into deterministic contract candidate evidence. Governance gates remain responsible for contract validation, authorization, routing, session attachment, replay validation, resilience certification, and promotion discipline.

The translation layer does not execute, authorize, route, attach, schedule, repair, learn, or mutate runtime state.

## Certification

`GOVERNED_PROPOSAL_TRANSLATION_LAYER_V1` certifies deterministic proposal-to-contract-candidate translation, replay-visible translation evidence, and governance authority separation without introducing execution authority, orchestration, autonomous cognition, semantic planning, runtime autonomy, or provider execution.
