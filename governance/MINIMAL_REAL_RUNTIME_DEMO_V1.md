# MINIMAL_REAL_RUNTIME_DEMO_V1

## Scope

This milestone implements the first minimal operational AiGOL runtime demo using the live governed cognition runtime.

The demo accepts a human request, invokes the bounded OpenAI connector, normalizes the proposal, routes it through the existing governed metadata execution path, validates production isolation evidence, normalizes the governed return, and emits replay-visible demo evidence.

It exposes:

- `run_minimal_real_runtime_demo(...)`
- `reconstruct_minimal_real_runtime_demo_lineage(...)`
- `MinimalRealRuntimeDemoEvidence`

## Demo Flow

The demonstrated path is:

Human request
→ OpenAI inference
→ governed proposal
→ cognition review
→ authorization/routing
→ readonly metadata provider execution
→ governed return
→ replay-visible evidence

## Runtime Boundary

The demo executes only the existing bounded readonly metadata path:

- provider: `metadata_inspection_provider`
- operation: `inspect_runtime`

Readonly filesystem and readonly HTTP capabilities remain outside this demo entrypoint unless future governed paths explicitly bind them.

## Guarantees

- Minimal runtime demo only.
- No orchestration introduced.
- No autonomous execution introduced.
- No runtime mutation introduced.
- No provider mutation introduced.
- Replay-visible operational evidence.
- Deterministic demo evidence hashing.
- Governed return display.
- Fail-closed malformed cognition handling.

## Non-Goals

- Workflow planning.
- Multi-agent runtime.
- Adaptive cognition.
- Provider mutation.
- Write execution.
- Retries.
- Async runtime.
- Shell execution.
- Subprocess execution.
- Workflow execution.

## Boundary

This layer composes existing governed runtime components into one minimal demo entrypoint. It does not add new provider authority, bypass governance review, mutate runtime state, perform retries, invoke async runtime, execute shell commands, spawn subprocesses, or introduce workflow execution.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`MINIMAL_REAL_RUNTIME_DEMO_V1` certifies a minimal real governed cognition execution demo, replay-visible operational evidence, governed return display, deterministic fail-closed containment, and governance authority separation without introducing orchestration, autonomous execution, runtime mutation, provider mutation, write execution, shell execution, or subprocess execution.
