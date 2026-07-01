# G8-04 ACLI Next Interactive Session Implementation V1

Status: ACLI Next interactive session implemented.

Final verdict: ACLI_NEXT_INTERACTIVE_SESSION_IMPLEMENTED

## 1. Executive Summary

G8-04 extends the G8-03 ACLI Next bootstrap into the first interactive runtime milestone.

The implementation adds a replay-visible multi-turn session loop for:

- clarification requests;
- human responses;
- proposal refinement turns;
- structured confirmation or rejection;
- fail-closed continuation checks.

ACLI Next remains a thin runtime entrypoint. It captures human input, delegates each turn to the existing PGSP-governed session entrypoint through the G8-03 bootstrap, records replay-visible session artifacts, and renders a bounded advisory summary.

G8-04 does not introduce repository mutation, Git operations, deployment, write-capable Workers, provider selection, or a new orchestration layer.

## 2. Implemented Runtime Surface

Files added:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/interactive.py` | Multi-turn ACLI Next session loop and interactive replay artifacts. |
| `tests/test_g8_acli_next_interactive_session.py` | Targeted tests for clarification continuation, terminal fail-closed behavior, and CLI routing. |
| `docs/governance/G8_04_ACLI_NEXT_INTERACTIVE_SESSION_IMPLEMENTATION_V1.md` | Governance implementation record. |

Files updated:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/__init__.py` | Exposes the interactive runtime API beside the bootstrap API. |
| `aigol/cli/aigol_cli.py` | Adds `aigol next interactive` and renders the interactive session summary. |

## 3. Interactive Session Model

The new runtime entrypoint is:

```text
aigol next interactive
```

The command accepts one or more structured turn arguments:

```text
--turn "human request=>human response"
```

Each turn is normalized into:

| Field | Meaning |
| --- | --- |
| `operator_request` | The human request or clarification response captured by ACLI Next. |
| `operator_response` | The structured human response, such as clarification, modification, confirmation, or rejection. |

ACLI Next then delegates each turn to:

```text
run_acli_next_session
```

`run_acli_next_session` continues to delegate semantic, orchestration, governance, and replay behavior to the certified PGSP lineage.

## 4. Clarification And Continuation Handling

The interactive runtime classifies continuation using the canonical response class returned by the PGSP-backed bootstrap turn.

Continuable response classes:

| Response Class | Meaning |
| --- | --- |
| `CLARIFICATION` | The session may continue with human clarification. |
| `MODIFICATION` | The session may continue with requested refinement. |
| `CONTINUATION` | The session may continue with another governed turn. |

Terminal response classes:

| Response Class | Meaning |
| --- | --- |
| `CONFIRMATION` | Advisory result is confirmed; no execution authorization is created. |
| `REJECTION` | Advisory result is rejected; the session closes. |

If a caller attempts another turn after a terminal response, ACLI Next fails closed before invoking another PGSP turn.

## 5. Replay Integration

G8-04 records the following replay-visible artifacts:

| Artifact | Purpose |
| --- | --- |
| `000_acli_next_interactive_started.json` | Captures interactive session start, declared turn count, workspace, and non-mutation flags. |
| `NNN_acli_next_turn_recorded.json` | Records each PGSP-backed bootstrap turn, canonical response class, continuation state, and replay references. |
| `NNN_acli_next_interactive_completed.json` | Records final interactive session summary, turn hashes, final response class, and replay reference. |

Turn-level PGSP evidence remains owned by the G8-03 bootstrap and the existing PGSP runtime. G8-04 indexes that evidence; it does not reconstruct or replace Replay.

## 6. Authority Analysis

G8-04 preserves certified authority boundaries:

| Authority | Preservation |
| --- | --- |
| PGSP | Owns governed session routing through the reused bootstrap path. |
| UBTR | Remains semantic translation authority behind PGSP. |
| CSA | Remains canonical semantic representation behind PGSP. |
| OCS | Remains proposal and orchestration owner behind PGSP. |
| Governance | Remains certification and admissibility authority. |
| Replay | Remains evidence reconstruction authority. |
| Worker Platform | Not invoked by G8-04. |
| EPP | Not invoked by G8-04. |
| ACLI Next | Captures, delegates, records, and renders only. |

No new authority layer, runtime registry, replay subsystem, Worker subsystem, or provider subsystem is introduced.

## 7. Governance Implications

The implementation is governance-preserving:

- each turn remains PGSP-governed;
- terminal responses block further continuation;
- confirmation remains advisory and does not create execution authorization;
- missing or mutating evidence fails closed;
- replay references are required for each turn;
- ACLI Next does not approve work, authorize execution, dispatch Workers, or invoke providers.

## 8. Replay Implications

Replay remains append-only and externally reconstructable through existing replay artifacts.

G8-04 adds replay-visible indexes for the interactive session shell:

- session start;
- turn sequence;
- response-class continuity;
- terminal state;
- final summary.

The runtime does not replay, rewrite, or infer PGSP evidence.

## 9. Fail-Closed Behavior

The interactive runtime fails closed when:

- no turns are provided;
- a turn is malformed;
- a turn is attempted after confirmation or rejection;
- PGSP-backed bootstrap output lacks replay evidence;
- PGSP-backed bootstrap output reports provider invocation;
- PGSP-backed bootstrap output reports Worker invocation;
- PGSP-backed bootstrap output reports approval, authorization, mutation, or deployment.

Fail-closed behavior prevents accidental escalation from advisory conversation into execution.

## 10. Deferred Functionality

The following remain intentionally deferred:

- repository mutation;
- Git command execution;
- patch application;
- commit creation;
- deployment;
- write-capable Worker execution;
- autonomous provider selection;
- autonomous Worker selection;
- long-running execution authorization reuse.

These require separate certification before adoption.

## 11. Validation Strategy

Required validation:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py
```

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py
```

Validation result: clean. Targeted pytest result: 6 passed.

## 12. Completion Criteria

Completion criteria:

| Criterion | Status |
| --- | --- |
| Interactive session loop exists. | Complete |
| Multi-turn clarification continuation is supported. | Complete |
| Terminal continuation fails closed. | Complete |
| Session history is replay-visible. | Complete |
| CLI route exists beside legacy ACLI. | Complete |
| PGSP remains delegated through bootstrap. | Complete |
| No repository mutation occurs. | Complete |
| No Git operation is introduced. | Complete |
| No Worker or provider invocation is introduced. | Complete |

## 13. Final Determination

G8-04 implements the first interactive ACLI Next runtime milestone.

The implementation extends ACLI Next from one advisory request to a governed, replay-visible, multi-turn session while preserving Platform Core authority boundaries and non-mutating behavior.

Final verdict: ACLI_NEXT_INTERACTIVE_SESSION_IMPLEMENTED
