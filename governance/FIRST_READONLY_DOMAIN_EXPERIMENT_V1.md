# FIRST_READONLY_DOMAIN_EXPERIMENT_V1

## Scope

This milestone implements the first readonly operational domain experiment on top of the completed AiGOL governed cognition runtime.

The chosen domain is:

- `Governance Runtime Inspector`

The chosen domain surface is:

- `readonly_runtime_metadata_inspection`

No other domain surface is combined in this milestone.

## Domain Flow

The experiment demonstrates:

Human request
→ OpenAI inference
→ governed proposal
→ cognition review
→ authorization/routing
→ readonly metadata provider
→ governed return
→ replay-visible evidence

## Runtime Boundary

The experiment reuses existing runtime infrastructure:

- live OpenAI runtime connector
- minimal real runtime demo
- governed cognition runtime
- readonly metadata provider
- governed return flow
- replay lineage

It does not introduce a new governance layer, runtime architecture, workflow engine, or domain execution controller.

## Guarantees

- Readonly domain experiment only.
- One domain surface only.
- No orchestration introduced.
- No autonomous execution introduced.
- Replay-visible operational evidence.
- Deterministic fail-closed containment.
- Governance authority separation preserved.
- Readonly containment preserved.

## Non-Goals

- New governance layer.
- Orchestration.
- Retries.
- Async runtime.
- Autonomous execution.
- Adaptive learning.
- Write execution.
- Shell execution.
- Subprocess execution.
- Workflow graphs.
- Multi-step planning.
- Session memory expansion.
- Agent behavior.

## Boundary

This layer validates practical readonly runtime usage. It does not bypass governance review, mutate runtime state, invoke orchestration, perform retries, invoke autonomous execution, execute writes, execute shell commands, spawn subprocesses, or expand session memory.

Governance authority remains deterministic, bounded, replay-visible, and fail-closed.

## Certification

`FIRST_READONLY_DOMAIN_EXPERIMENT_V1` certifies a readonly domain experiment only, replay-visible operational evidence, deterministic fail-closed containment, and governance authority separation without introducing orchestration, autonomous execution, runtime mutation, provider mutation, write capability, workflow planning, or agent behavior.
