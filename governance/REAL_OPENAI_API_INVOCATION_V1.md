# REAL_OPENAI_API_INVOCATION_V1

## Scope

This milestone implements the first real OpenAI API invocation boundary inside AiGOL.

The invocation layer uses the official OpenAI Python SDK and the Responses API, loads `OPENAI_API_KEY` from the environment, performs one synchronous bounded inference request, and sends the model response through the existing governed OpenAI connector.

It exposes:

- `invoke_real_openai_api(...)`
- `reconstruct_real_openai_api_invocation_lineage(...)`
- `RealOpenAIAPIInvocationEvidence`

## API Boundary

The invocation is fixed to:

- provider: `openai`
- model identifier: `gpt-5.5`
- API key environment variable: `OPENAI_API_KEY`
- Responses API
- synchronous invocation only
- bounded timeout
- `max_retries=0`
- readonly metadata proposal only

## Flow

Human request
→ real OpenAI API inference
→ bounded cognition proposal
→ proposal translation
→ cognition review
→ authorization/routing
→ readonly metadata provider
→ governed return
→ replay-visible evidence

## Guarantees

- Real OpenAI API invocation only.
- No orchestration introduced.
- No autonomous execution introduced.
- Replay-visible inference lineage.
- Deterministic fail-closed normalization.
- Governance authority separation preserved.
- Readonly bounded cognition runtime preserved.
- Missing API key fails closed.
- Malformed model output fails closed.
- Unauthorized capability proposals fail closed.

## Non-Goals

- Orchestration systems.
- Autonomous cognition.
- Retries.
- Streaming.
- Workflow planning.
- Provider mutation.
- Adaptive policy learning.
- Runtime autonomy.
- Self-modifying governance.
- Multi-agent coordination.
- Write execution.
- Shell execution.
- Subprocess execution.

## Boundary

This layer performs one bounded OpenAI Responses API call and then delegates normalization to existing governance surfaces. It does not execute providers directly outside governance, bypass cognition review, mutate runtime state, invoke orchestration, invoke retries, or invoke autonomous execution.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`REAL_OPENAI_API_INVOCATION_V1` certifies real OpenAI API invocation only, replay-visible inference lineage, deterministic fail-closed normalization, governance authority separation, and readonly bounded cognition runtime preservation without introducing orchestration, autonomous execution, retries, streaming, runtime mutation, provider mutation, write execution, shell execution, or subprocess execution.
