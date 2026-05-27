# LIVE_EXTERNAL_LLM_PROVIDER_V1

## Scope

This milestone implements the first live external LLM provider boundary for AiGOL.

The provider accepts a bounded human prompt, normalizes a deterministic inference request, invokes one supplied synchronous external inference source, validates the model output, and normalizes it into existing bounded cognition proposal evidence.

It exposes:

- `invoke_live_external_llm_provider(...)`
- `reconstruct_live_external_llm_inference_lineage(...)`
- `LiveExternalLLMInferenceEvidence`

## Provider Boundary

The live provider is fixed to:

- `external_llm_provider`
- `bounded-proposal-model`
- synchronous inference only
- bounded proposal output only
- readonly metadata capability only: `metadata_inspection_provider.inspect_runtime`

The provider produces replay-visible inference evidence and delegates proposal normalization to the existing external LLM attachment layer.

## Guarantees

- Live external inference only.
- No execution authority introduced.
- No orchestration introduced.
- Replay-visible inference lineage.
- Deterministic fail-closed normalization.
- Governance authority separation preserved.
- Unauthorized capability proposals fail closed.

## Non-Goals

- Autonomous cognition.
- Workflow planning.
- Orchestration systems.
- Provider mutation.
- Adaptive policy learning.
- Runtime autonomy.
- Self-modifying governance.
- Multi-agent coordination.
- Streaming inference.
- Async inference.
- Retries.
- Memory persistence.
- Tool autonomy.

## Boundary

This layer connects one live external inference source to bounded proposal normalization. It does not execute providers directly, authorize execution, bypass governance review, mutate runtime state, invoke orchestration, invoke async runtime, perform retries, or introduce autonomous execution.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`LIVE_EXTERNAL_LLM_PROVIDER_V1` certifies live external inference only, replay-visible inference lineage, deterministic fail-closed normalization, and governance authority separation without introducing execution authority, orchestration, autonomous cognition, provider execution authority, or runtime mutation.
