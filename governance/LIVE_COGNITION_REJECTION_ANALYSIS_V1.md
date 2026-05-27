# LIVE_COGNITION_REJECTION_ANALYSIS_V1

## Scope

This milestone is a debugging and stabilization layer for the existing live governed cognition runtime. It adds the minimal readonly inspection visibility required to diagnose why valid readonly operator requests are being rejected.

It exposes:

- `analyze_live_cognition_rejection(...)`
- `reconstruct_live_cognition_rejection_analysis_lineage(...)`
- `render_rejection_analysis_summary(...)`
- `LiveCognitionRejectionAnalysisEvidence`
- `run_live_cognition_rejection_analysis_cli(...)`
- a CLI surface under `python -m aigol.runtime.live_cognition_rejection_analysis_cli`

The analyzer inspects a single live runtime usage record produced by the existing
`validate_live_runtime_usage` entrypoint and surfaces, in one replay-visible
artifact, the following six rejection-diagnostic fields:

1. raw OpenAI output (the bounded JSON proposal payload preserved by the live OpenAI connector)
2. normalized cognition proposal (the bounded `BoundedCognitionProposal` evidence)
3. cognition review decision (`REVIEWED` or `REJECTED` with reason and risk level)
4. authorization decision (`AUTHORIZED` or `REJECTED` with requested, authorized, and rejected provider sets)
5. routing decision (`ROUTED` or `REJECTED` with reason)
6. exact rejection reason (the first failing stage of the live governed pipeline)

## Boundary

The analyzer is strictly readonly. It does not invoke the OpenAI API, does not
reach providers, does not mutate runtime state, does not mutate provider state,
does not retry, and does not introduce orchestration. It only inspects evidence
that has already been preserved by the live governed cognition runtime and
re-projects it into a single replay-visible diagnostic record.

The CLI surface drives one prompt through the existing
`validate_live_runtime_usage` entrypoint and then runs the analyzer over the
single resulting usage record. No new execution authority is introduced.

## Reused Runtime Infrastructure

- live OpenAI runtime connector
- real OpenAI API invocation
- live runtime usage validation
- governed cognition review gate
- governed contract authorization gate
- governed contract router
- production isolation foundation
- governed return interpretation
- bounded LLM attachment architecture
- replay-visible transport serialization

No new providers, no new gates, no new execution authority, and no new
orchestration surfaces are introduced.

## Guarantees

- Readonly inspection only.
- Fail-closed on missing or malformed usage records.
- Replay-visible deterministic evidence (canonical hash, `from_dict`/`to_dict` round trip).
- Append-only analysis lineage with stable ordering.
- Governance authority separated.
- No new execution authority introduced.

## Non-Goals

- New runtime architecture.
- New capability layers.
- New orchestration surfaces.
- Retries.
- Async runtime.
- Runtime mutation.
- Provider mutation.
- New telemetry platform.
- Autonomous execution.
- Workflow planning.
- Capability expansion.

## Inspection Stages

The analyzer assigns one of the following `rejection_stage` values to each
analyzed usage record:

- `NONE` — usage validated through the full governed path.
- `USAGE_INPUT` — the usage record itself was missing or malformed.
- `OPENAI_INVOCATION` — the live OpenAI connector did not normalize a bounded proposal payload.
- `GOVERNED_EXECUTION` — governed execution evidence was absent after a normalized proposal.
- `COGNITION_REVIEW` — the cognition review gate rejected the translated contract candidate.
- `CONTRACT_AUTHORIZATION` — the authorization gate rejected the contract against the session policy.
- `CONTRACT_ROUTING` — the contract router rejected the authorized contract.
- `PRODUCTION_ISOLATION` — production isolation did not validate execution containment.
- `GOVERNED_RETURN` — the governed return interpretation did not accept the provider return evidence.

The stage is the deepest live runtime evidence layer that did not produce its
expected `VALIDATED`-equivalent state. The accompanying `rejection_reason` is
copied verbatim from that layer's evidence so the diagnostic record carries
deterministic forensic context.

## Certification

`LIVE_COGNITION_REJECTION_ANALYSIS_V1` certifies minimal readonly rejection
inspection visibility over the live governed cognition runtime, replay-visible
deterministic evidence preservation, fail-closed containment preservation, and
governance authority separation without introducing new runtime architecture,
new capability layers, orchestration, retries, async runtime, runtime mutation,
provider mutation, new telemetry platform, autonomous execution, or capability
expansion.
