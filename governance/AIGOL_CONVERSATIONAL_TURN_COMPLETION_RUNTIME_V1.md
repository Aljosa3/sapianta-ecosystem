# AIGOL_CONVERSATIONAL_TURN_COMPLETION_RUNTIME_V1

## Status

Certified conversational turn completion runtime.

Classification:

```text
CERTIFIED_CONVERSATIONAL_TURN_COMPLETION_RUNTIME
```

## Purpose

This runtime adds explicit lifecycle semantics to the interactive
`aigol conversation` loop after a turn has executed and replay progress has
been recorded.

It makes these states replay-visible:

- `TURN_COMPLETED`;
- `RESULT_DELIVERED`.

No cognition runtime was changed. No provider behavior was changed. No OCS
cognition behavior was changed. No governance authority was expanded.

## Lifecycle Transitions

The certified lifecycle extension is:

```text
PROMPT_READ
-> PROMPT_NORMALIZED
-> TURN_ALLOCATED
-> ROUTED
-> BRANCH_EXECUTED
-> RESULT_ASSEMBLED
-> REPLAY_PROGRESS_RECORDED
-> TURN_COMPLETED
-> RESULT_DELIVERED
-> LOOP_REENTRY
```

### TURN_COMPLETED

`TURN_COMPLETED` means the turn branch has finished, the result has been
assembled, and the conversational progress replay has reached `Replay` with
the turn status.

Artifact:

```text
TURN_COMPLETED_ARTIFACT_V1
```

### RESULT_DELIVERED

`RESULT_DELIVERED` means the human-facing result has been written to the
operator output stream and the completion boundary has been recorded.

Artifact:

```text
RESULT_DELIVERED_ARTIFACT_V1
```

## Replay Evidence

Each completed turn persists immutable replay evidence under:

```text
<runtime_root>/<session_id>/<turn_id>/turn_completion/
```

Replay files:

```text
000_turn_completed.json
001_result_delivered.json
```

Replay reconstruction verifies:

- replay ordering;
- wrapper hashes;
- artifact hashes;
- result-delivery reference continuity;
- turn-completion hash continuity;
- explicit `result_delivered: true`.

## Operator Summary

After successful turn execution, the CLI emits an operator-visible boundary:

```text
================================
TURN COMPLETED
turn_id: TURN-000001
providers: ...
status: COMPLETED
result_delivered: TRUE
elapsed: 8s
============
```

The next `AiGOL >` prompt appears only after this boundary.

## Boundary Preservation

This runtime is visibility-only.

It does not:

- invoke providers;
- dispatch workers;
- request execution;
- approve execution;
- mutate governance;
- mutate existing replay;
- terminate or alter the interactive REPL contract.

The REPL still re-enters after completed turns. The difference is that the
operator now receives explicit completion and result-delivery evidence before
the next prompt.

## Acceptance

Accepted when:

- `TURN_COMPLETED_ARTIFACT_V1` is persisted;
- `RESULT_DELIVERED_ARTIFACT_V1` is persisted;
- replay reconstruction proves both artifacts;
- the turn summary exposes `turn_completed: true`;
- the turn summary exposes `result_delivered: true`;
- the operator-facing completion block renders before loop reentry;
- existing cognition, provider, comparison, continuity, clarification, and
  replay boundaries remain unchanged.
