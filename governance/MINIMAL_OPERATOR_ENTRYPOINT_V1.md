# Minimal Operator Entrypoint V1

Status: first useful AiGOL usability milestone.

This artifact defines the simplest practical operator entrypoint into the frozen operational epoch. It introduces no orchestration, agent runtime, new capability, capability expansion, memory, or routing.

## Primary Question

How does a human actually use AiGOL?

## Answer

A human uses AiGOL by submitting one bounded request to the minimal operator entrypoint. The entrypoint invokes the existing frozen governed read-only runtime and returns a concise governed result summary.

## Flow

```text
Human
-> submit request
-> governed processing
-> governed result
```

The expanded governed path remains:

```text
Human request
-> cognition proposal
-> AiGOL proposal normalization
-> AiGOL validation
-> AiGOL authorization
-> governed execution request
-> deterministic worker/runtime execution
-> read-only capability result
-> replay-visible evidence
-> governed return
-> operator summary
```

## Supported Capabilities

The entrypoint may target only existing frozen capabilities:

- `READ_ONLY_RUNTIME_INSPECTION`
- `FILESYSTEM_READ_ONLY_INSPECTION`

## Non-Goals

The entrypoint does not introduce:

- orchestration
- agent runtime
- new capability
- capability expansion
- memory
- routing
- shell execution
- network execution
- filesystem mutation

## Success

Success is a clear and minimal way for a human operator to use AiGOL while preserving:

```text
LLM proposes.
AiGOL governs.
Worker executes.
Replay records.
```
