# REAL_EXTERNAL_LLM_ATTACHMENT_V1

## Scope

This milestone implements the first real external LLM attachment boundary for AiGOL.

The attachment accepts externally produced model response evidence, validates its replay hash, validates bounded proposal structure, and normalizes it into existing bounded cognition proposal artifacts.

It exposes:

- `attach_external_llm_response(...)`
- `external_model_response_hash(...)`
- `reconstruct_external_llm_proposal_lineage(...)`

## Attachment Boundary

The accepted external model response contains:

- `model_response_id`
- `model_provider`
- `model_name`
- `proposal_payload`
- `created_at`
- `response_hash`

The normalized output is a bounded cognition proposal artifact.

## Guarantees

- External LLM attachment only.
- No execution authority introduced.
- No orchestration introduced.
- Replay-visible cognition lineage.
- Deterministic fail-closed normalization.
- Governance authority separation preserved.
- No external provider invocation by this layer.

## Non-Goals

- Autonomous cognition.
- Workflow planning.
- Orchestration systems.
- Provider mutation.
- Adaptive policy learning.
- Runtime autonomy.
- Self-modifying governance.
- Multi-agent coordination.
- Execution delegation.

## Boundary

This layer attaches externally obtained model inference output. It does not call external LLM APIs, execute providers, authorize execution, bypass governance review, mutate runtime state, invoke orchestration, invoke async runtime, or perform autonomous retries.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`REAL_EXTERNAL_LLM_ATTACHMENT_V1` certifies external LLM attachment only, replay-visible cognition lineage, deterministic fail-closed normalization, and governance authority separation without introducing execution authority, orchestration, autonomous cognition, provider execution, or runtime mutation.
