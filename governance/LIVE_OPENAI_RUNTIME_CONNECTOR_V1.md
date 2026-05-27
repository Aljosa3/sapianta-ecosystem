# LIVE_OPENAI_RUNTIME_CONNECTOR_V1

## Scope

This milestone implements the first live OpenAI runtime connector for AiGOL.

The connector builds a deterministic OpenAI inference request, accepts a supplied synchronous OpenAI call surface, parses bounded JSON model output, and normalizes it into existing bounded cognition proposal evidence.

It exposes:

- `invoke_live_openai_runtime_connector(...)`
- `reconstruct_live_openai_runtime_lineage(...)`
- `LiveOpenAIRuntimeConnectorEvidence`

## Connector Boundary

The connector is fixed to:

- OpenAI provider: `openai`
- model identifier: `gpt-5.5`
- synchronous inference only
- bounded proposal JSON output only
- readonly metadata capability only: `metadata_inspection_provider.inspect_runtime`

The connector produces replay-visible inference evidence and delegates proposal normalization to the existing external LLM attachment layer.

## Guarantees

- Live OpenAI inference only.
- No execution authority introduced.
- No orchestration introduced.
- Replay-visible inference lineage.
- Deterministic fail-closed normalization.
- Governance authority separation preserved.
- Unauthorized capability proposals fail closed.

## Non-Goals

- Autonomous execution.
- Workflow planning.
- Agent runtime.
- Provider mutation.
- Execution delegation.
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

This layer connects one OpenAI inference surface to bounded proposal normalization. It does not execute providers directly, bypass governance review, mutate runtime state, invoke orchestration, invoke async runtime, perform retries, or introduce autonomous execution.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`LIVE_OPENAI_RUNTIME_CONNECTOR_V1` certifies live OpenAI inference only, replay-visible inference lineage, deterministic fail-closed normalization, and governance authority separation without introducing execution authority, orchestration, autonomous cognition, provider execution authority, or runtime mutation.
