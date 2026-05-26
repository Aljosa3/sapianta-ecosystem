# MINIMAL_REAL_LLM_PROPOSAL_FLOW_V1

## Scope

This milestone implements the first real-LLM-facing bounded proposal flow for AiGOL.

The flow accepts bounded natural-language proposal input and normalizes it into existing bounded cognition proposal artifacts. It does not call an LLM provider, authorize execution, execute providers, attach contracts, mutate runtime state, or bypass governance review.

It exposes:

- `normalize_real_llm_proposal_input(...)`
- `reconstruct_real_llm_proposal_lineage(...)`

## Proposal Flow

The accepted input structure is:

- `proposal_id`
- `natural_language_input`
- `proposal_type`
- `requested_capabilities`
- `proposed_contract_reference`
- `created_at`

The normalized output is a bounded cognition proposal artifact with replay-visible evidence.

## Guarantees

- Bounded LLM proposal flow only.
- No execution authority introduced.
- No orchestration introduced.
- Replay-visible proposal lineage.
- Governance authority separation preserved.
- No autonomous cognition introduced.
- Deterministic proposal normalization.

## Non-Goals

- Autonomous cognition.
- Semantic planning.
- Orchestration systems.
- Workflow execution.
- Provider execution.
- Adaptive policy learning.
- Runtime autonomy.
- Self-modifying governance.
- Multi-agent coordination.

## Boundary

A real LLM may provide bounded proposal text and declared bounded capability requests. The proposal flow normalizes that input into governed proposal evidence only.

Governance remains responsible for proposal translation, cognition review, contract validation, authorization, routing, replay validation, resilience certification, and promotion discipline.

## Certification

`MINIMAL_REAL_LLM_PROPOSAL_FLOW_V1` certifies bounded LLM proposal intake, replay-visible proposal lineage, deterministic normalization, and governance authority separation without introducing execution authority, orchestration, autonomous cognition, runtime mutation, or provider execution.
