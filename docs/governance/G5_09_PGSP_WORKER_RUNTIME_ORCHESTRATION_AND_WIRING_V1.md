# G5-09 PGSP Worker Runtime Orchestration And Wiring V1

Status: implemented.

Final verdict: G5_09_READY

## 1. Purpose

G5-09 implements the minimal PGSP orchestration layer that connects a certified execution authorization handoff to the existing Worker runtime stack.

This is wiring, not Worker redesign. PGSP does not create a new Worker architecture, duplicate Worker authorization, duplicate Worker replay, or duplicate Worker identity.

The canonical implementation rule is:

```text
PGSP orchestrates the certified Worker stack.
Worker Services still own Worker request, identity, assignment, dispatch, invocation, result capture, validation, and post-execution review.
```

## 2. Implemented Runtime

Implemented runtime:

```text
aigol/runtime/g5_pgsp_worker_runtime_orchestration.py
```

Public entrypoints:

- `run_g5_pgsp_worker_runtime_orchestration(...)`
- `reconstruct_g5_pgsp_worker_orchestration_replay(...)`

The runtime accepts:

- PGSP session id;
- execution authorization replay reference;
- requested actor;
- creation timestamp;
- replay directory;
- optional Worker registry artifacts.

The runtime returns a PGSP Worker orchestration capture containing:

- orchestration status;
- Worker runtime phase statuses;
- governance checkpoint status;
- UHCL summary status;
- replay reference;
- summary artifact;
- non-duplication flags;
- failure reason when fail-closed.

## 3. Reused Worker Components

G5-09 reuses the existing certified Worker stack in order:

| Phase | Existing Runtime | Reuse Role |
| --- | --- | --- |
| Authorization-to-Worker request | `worker_invocation_request_runtime.py` | Consumes execution authorization replay and creates Worker invocation request. |
| Worker identity and capability assignment | `worker_assignment_runtime.py` | Selects compatible Worker from registry evidence. |
| Worker dispatch | `worker_dispatch_runtime.py` | Dispatches assigned Worker without changing Worker identity rules. |
| Worker invocation | `worker_invocation_runtime.py` | Invokes dispatched Worker and records invocation evidence. |
| Execution start | `execution_runtime.py` | Records deterministic execution start. |
| Worker output capture | `worker_result_capture_runtime.py` | Captures Worker output and binds it to execution evidence. |
| Result validation | `worker_result_validation_runtime.py` | Validates captured Worker result. |
| Post-execution review | `post_execution_replay_review_runtime.py` | Reviews replay, output, and authority continuity. |

No Worker runtime module was redesigned.

## 4. Orchestration Flow

The implemented PGSP flow is:

```text
PGSP session context
-> execution authorization replay reference
-> existing Worker invocation request runtime
-> existing Worker assignment runtime
-> existing Worker dispatch runtime
-> existing Worker invocation runtime
-> existing execution runtime
-> existing Worker result capture runtime
-> existing Worker result validation runtime
-> existing post-execution replay review runtime
-> PGSP governance checkpoint summary
-> UHCL Worker execution summary marker
-> replay reconstruction
```

The execution runtime's certified actor boundary is preserved: execution start is recorded by `AIGOL`, while the PGSP requested actor remains replay-visible in execution context.

## 5. Replay Evidence

G5-09 adds two PGSP-level replay artifacts:

```text
000_pgsp_worker_orchestration_context_recorded.json
001_pgsp_worker_orchestration_summary_recorded.json
```

The summary artifact stores nested replay references for:

- Worker invocation request;
- Worker assignment;
- Worker dispatch;
- Worker invocation;
- execution start;
- Worker result capture;
- Worker result validation;
- post-execution replay review.

Replay reconstruction verifies:

- PGSP wrapper ordering;
- PGSP wrapper hashes;
- PGSP artifact hashes;
- context-to-summary lineage;
- non-duplication and non-mutation flags;
- nested Worker replay reconstruction;
- nested replay reconstruction hash.

## 6. Governance Evidence

The PGSP summary emits:

```text
G5_09_PGSP_WORKER_ORCHESTRATION_GOVERNANCE_PASSED
```

when all existing Worker phases complete through post-execution review.

Failure emits:

```text
G5_09_PGSP_WORKER_ORCHESTRATION_GOVERNANCE_FAILED_CLOSED
```

The runtime preserves fail-closed behavior from downstream Worker runtimes and carries downstream failure reasons into the PGSP summary.

Governance boundaries preserved:

- no provider invocation;
- no Worker self-authorization;
- no duplicate Worker authorization;
- no duplicate Worker replay model;
- no duplicate Worker identity model;
- no governance mutation;
- no replay mutation;
- no retry or fallback;
- no deployment.

## 7. UHCL Summary Evidence

The PGSP summary emits:

```text
G5_09_UHCL_WORKER_EXECUTION_SUMMARY_AVAILABLE
```

for completed orchestration and:

```text
G5_09_UHCL_WORKER_EXECUTION_SUMMARY_FAILED_CLOSED
```

for failed-closed orchestration.

This is a PGSP-visible UHCL review marker. Interfaces render the summary; they do not generate reusable communication.

## 8. Failure Handling

The runtime fails closed when:

- execution authorization replay is missing;
- execution authorization is expired;
- any Worker phase fails closed;
- replay directory is not empty;
- PGSP replay hashes are corrupted;
- PGSP boundary flags indicate unauthorized mutation or duplication;
- nested Worker replay reconstruction does not match summary evidence.

Failure does not assign, dispatch, invoke, retry, fallback, deploy, or mutate governance outside the successfully completed certified phases.

## 9. Ownership Matrix

| Capability | Owner | G5-09 Behavior |
| --- | --- | --- |
| PGSP session context | PGSP | Records context and orchestration summary. |
| Execution authorization validation | Authorization / Worker request runtime | Reused; not duplicated. |
| Worker request package | Worker Services | Reused through Worker invocation request runtime. |
| Worker identity assignment | Worker Services | Reused through Worker assignment runtime. |
| Worker dispatch | Worker Services / dispatch runtime | Reused. |
| Worker invocation | Worker Services | Reused. |
| Execution start | Execution runtime | Reused. |
| Result capture | Worker Services / Replay | Reused. |
| Result validation | Worker Services / Governance | Reused. |
| Post-execution review | Replay / Governance | Reused. |
| Human communication | UHCL | PGSP emits UHCL summary status for rendering. |
| Interface rendering | Adapter | Unchanged. |

## 10. Validation Evidence

Validation commands:

```bash
python -m py_compile aigol/runtime/g5_pgsp_worker_runtime_orchestration.py tests/test_g5_pgsp_worker_runtime_orchestration.py
python -m pytest tests/test_g5_pgsp_worker_runtime_orchestration.py
python -m pytest tests/
git diff --check
```

Targeted validation result:

```text
5 passed
```

Full validation result:

```text
5596 passed, 1 skipped
```

Diff validation result:

```text
git diff --check passed
```

## 11. Remaining Execution Blockers

Remaining blockers are outside G5-09:

- domain-specific rollback policy before broader mutating Worker classes;
- durable UHCL rendering surface for multi-adapter execution summaries;
- future authorization consumption policy for single-use authorization across long-lived sessions;
- future production Worker capability certification beyond the deterministic existing stack.

These are not blockers for PGSP-to-Worker orchestration wiring.

## 12. Rollback Impact

Rollback is low impact:

- remove `aigol/runtime/g5_pgsp_worker_runtime_orchestration.py`;
- remove `tests/test_g5_pgsp_worker_runtime_orchestration.py`;
- remove this governance artifact.

No existing Worker runtime behavior is changed.

## 13. Certification Impact

G5-09 certifies that PGSP can invoke the existing Worker runtime stack through governed orchestration while preserving:

- PGSP session ownership;
- Worker Service ownership;
- authorization boundaries;
- replay visibility;
- governance checkpoints;
- UHCL summary visibility;
- fail-closed behavior.

Final verdict: G5_09_READY
