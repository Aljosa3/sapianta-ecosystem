# G8-06 Execution Plan And Mutation Preview V1

Status: ACLI Next execution plan implemented.

Final verdict: ACLI_NEXT_EXECUTION_PLAN_IMPLEMENTED

## 1. Executive Summary

G8-06 introduces deterministic execution planning for ACLI Next without repository mutation.

After a confirmed ACLI Next interactive session, ACLI Next can now produce a replay-visible advisory execution plan describing:

- selected Worker sequence;
- requested capabilities;
- expected artifacts;
- potential repository impact;
- replay plan;
- governance checkpoints;
- execution risk summary;
- descriptive mutation preview.

The implementation does not execute mutating Workers, modify repository contents, create commits, deploy, invoke providers, or authorize execution.

## 2. Implemented Runtime Surface

Files added:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/execution_plan.py` | Advisory execution plan and descriptive mutation preview runtime. |
| `tests/test_g8_acli_next_execution_plan.py` | Targeted tests for planning, fail-closed confirmation, duplicate evidence, and CLI routing. |
| `docs/governance/G8_06_EXECUTION_PLAN_AND_MUTATION_PREVIEW_V1.md` | Governance implementation record. |

Files updated:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/__init__.py` | Exposes the execution plan runtime APIs. |
| `aigol/cli/aigol_cli.py` | Adds `aigol next execution-plan` and renders execution plan summaries. |

## 3. Runtime Entry Point

The new CLI route is:

```text
aigol next execution-plan
```

The command reuses the G8-04 interactive turn model:

```text
--turn "human request=>human response"
```

Optional planning inputs:

| Argument | Purpose |
| --- | --- |
| `--worker-step` | Adds a selected Worker sequence entry. |
| `--capability` | Adds a requested capability. |
| `--expected-artifact` | Adds an expected artifact. |
| `--potential-impact` | Adds descriptive repository impact text. |

If optional inputs are omitted, the runtime uses conservative advisory defaults.

## 4. Execution Plan Model

The execution plan artifact contains:

| Field | Meaning |
| --- | --- |
| `selected_worker_sequence` | Planned Worker sequence, not executed. |
| `requested_capabilities` | Capabilities required by the future execution path. |
| `expected_artifacts` | Artifacts expected from future execution. |
| `potential_repository_impact` | Descriptive-only repository impact. |
| `replay_plan` | Planned replay artifacts and Replay ownership statement. |
| `governance_checkpoints` | Required governance gates before future execution. |
| `execution_risk_summary` | Risk classification and certification requirements. |
| `mutation_preview_required` | Always true for G8-06. |

The plan is advisory and replay-visible.

## 5. Mutation Preview

The mutation preview is descriptive only.

It records:

- `descriptive_only: true`;
- `repository_files_to_modify: []`;
- `git_operations: []`;
- `deployment_operations: []`;
- potential repository impact text;
- future mutation certification requirement.

No patch is generated, no file is edited, no Git command is executed, and no deployment is performed.

## 6. Governance Integration

Planning requires:

| Check | Required State |
| --- | --- |
| Interactive session status | `ACLI_NEXT_INTERACTIVE_COMPLETED` |
| Final response class | `CONFIRMATION` |
| Replay evidence | `replay_reference` and `replay_hash` present |
| Provider invocation | `False` |
| Worker invocation | `False` |
| Execution authorization | `False` |
| Repository mutation | `False` |
| Deployment | `False` |

The governance authorization status is:

```text
AUTHORIZED_ADVISORY_EXECUTION_PLAN
```

This authorizes only advisory planning and descriptive mutation preview. It does not authorize execution.

## 7. Replay Integration

G8-06 records:

| Artifact | Purpose |
| --- | --- |
| `000_acli_next_execution_plan_request.json` | Captures planning request and governance authorization reference. |
| `001_acli_next_execution_plan_recorded.json` | Captures the advisory execution plan. |
| `002_acli_next_mutation_preview_recorded.json` | Captures descriptive mutation preview. |
| `003_acli_next_execution_plan_completed.json` | Captures final plan summary and replay reference. |

Replay remains append-only and authoritative. ACLI Next records planning evidence but does not reconstruct or mutate Replay.

## 8. Authority Analysis

G8-06 preserves Platform Core boundaries:

| Authority | Preservation |
| --- | --- |
| PGSP | Interactive session still routes through G8-04 and G8-03 PGSP delegation. |
| UBTR | Not duplicated. |
| CSA | Not duplicated. |
| OCS | Not duplicated. |
| Governance | Provides the advisory planning boundary. |
| Replay | Remains evidence reconstruction authority. |
| Worker Platform | Planned only; no Worker is invoked. |
| EPP | Not invoked. |
| ACLI Next | Captures, plans, records, and renders only. |

## 9. Fail-Closed Behavior

The runtime fails closed when:

- interactive session is incomplete;
- human confirmation is missing;
- replay evidence is missing;
- prior provider invocation is detected;
- prior Worker invocation is detected;
- execution authorization is present;
- repository mutation is present;
- deployment is present;
- planning lists are empty, malformed, or contain duplicates.

## 10. Deferred Functionality

Deferred beyond G8-06:

- mutating Worker execution;
- patch generation;
- file edits;
- Git commits;
- deployment;
- provider invocation;
- autonomous Worker selection;
- execution authorization reuse.

These require separate certification.

## 11. Validation Strategy

Required validation:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/acli_next/readonly_worker.py aigol/acli_next/execution_plan.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py tests/test_g8_acli_next_execution_plan.py
```

Validation performed:

```text
git diff --check
python -m py_compile aigol/acli_next/__init__.py aigol/acli_next/entrypoint.py aigol/acli_next/interactive.py aigol/acli_next/readonly_worker.py aigol/acli_next/execution_plan.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py tests/test_g8_acli_next_execution_plan.py
```

Validation result: clean. Targeted pytest result: 14 passed.

## 12. Completion Criteria

Completion criteria:

| Criterion | Status |
| --- | --- |
| Execution plan model exists. | Complete |
| Plan requires confirmed interactive session. | Complete |
| Selected Worker sequence is recorded. | Complete |
| Requested capabilities are recorded. | Complete |
| Expected artifacts are recorded. | Complete |
| Potential repository impact is described only. | Complete |
| Replay plan is recorded. | Complete |
| Governance checkpoints are recorded. | Complete |
| Execution risk summary is recorded. | Complete |
| Mutation preview is descriptive only. | Complete |
| No Worker is invoked. | Complete |
| No provider is invoked. | Complete |
| No repository mutation occurs. | Complete |
| No Git operation is introduced. | Complete |
| No deployment occurs. | Complete |

## 13. Final Determination

G8-06 implements deterministic advisory execution planning and descriptive mutation preview for ACLI Next.

The implementation prepares future execution work without crossing into execution, mutation, deployment, provider invocation, or Worker dispatch.

Final verdict: ACLI_NEXT_EXECUTION_PLAN_IMPLEMENTED
