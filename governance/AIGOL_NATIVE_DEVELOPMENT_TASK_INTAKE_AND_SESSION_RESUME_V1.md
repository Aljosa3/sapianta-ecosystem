# AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_AND_SESSION_RESUME_V1

## Status

Implementation certification artifact.

## Purpose

This milestone implements the first corrective native-development runtime layer after:

```text
AIGOL_NATIVE_DEVELOPMENT_READINESS_STATUS = PARTIAL
```

It allows conversation mode to:

- resume existing append-only conversation sessions;
- allocate the next unused turn id;
- avoid source router replay collisions;
- recognize native development-intent prompts;
- record replay-visible task intake evidence;
- return safe operator-facing handoff guidance.

It does not implement domains, workers, governance artifact creation, execution, dispatch, or provider-controlled development.

## Runtime Components

Implemented runtimes:

- `aigol/runtime/conversation_session_resume_runtime.py`;
- `aigol/runtime/native_development_task_intake_runtime.py`.

Updated CLI surface:

- `python -m aigol.cli.aigol_cli conversation`.

## Session Resume Semantics

Conversation mode now inspects:

```text
<runtime-root>/<session-id>/TURN-*
```

and allocates the next unused id:

```text
TURN-000001
TURN-000002
TURN-000003
...
```

This prevents reused default sessions from attempting to rewrite:

```text
000_source_of_truth_router_selected.json
001_source_of_truth_router_returned.json
```

The source router remains append-only and fail-closed.

## Native Development Task Intake

Development prompts now create:

```text
AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_ARTIFACT_V1
```

The artifact records:

- requested milestone id;
- requested domain when detectable;
- requested worker family when detectable;
- requested output scope;
- explicit constraints;
- task kind;
- native development safety;
- Codex-assisted handoff requirement;
- suggested next safe handoff.

## Fail-Closed Conditions

The intake runtime fails closed when:

- no single milestone id can be identified;
- requested scope is ambiguous;
- request implies prohibited authority;
- request implies dispatch, invocation, execution, order placement, broker integration, exchange integration, live trading, governance mutation, or replay mutation;
- replay path collision would occur.

## Authority Boundaries

The runtime does not:

- create governance artifacts;
- modify governance;
- create workers;
- create domains;
- create execution requests;
- dispatch workers;
- invoke workers;
- execute operations;
- mutate replay outside append-only intake evidence.

Authority preservation:

```text
LLM proposes
AiGOL governs
Human authorizes
Worker executes
Replay records
```

## Operator Output

For recognized native development tasks, conversation mode returns:

- recognized development task status;
- milestone id;
- domain;
- worker family;
- task kind;
- explicit constraints;
- safety status;
- Codex-assisted handoff requirement;
- suggested next safe handoff.

## Replay

Intake replay is reconstructable through:

```text
reconstruct_native_development_task_intake_replay(...)
```

Replay steps:

```text
000_native_development_task_intake_recorded.json
001_native_development_task_intake_returned.json
```

## Final Classification

```text
AIGOL_NATIVE_DEVELOPMENT_TASK_INTAKE_AND_SESSION_RESUME_STATUS = CERTIFIED
```

