# G8-06B Platform Core Execution Plan Preview Service V1

Status: Platform Core execution planning canonicalized.

Final verdict: PLATFORM_CORE_EXECUTION_PLANNING_CANONICALIZED

## 1. Executive Summary

G8-06B corrects the thin-entrypoint leakage identified by G8-06A.

G8-05 and G8-06 introduced bounded, non-mutating advisory behavior inside ACLI Next. The behavior was replay-visible and safe, but several responsibilities belonged to Platform Core rather than a human-interface adapter.

G8-06B moves those responsibilities behind a reusable Platform Core service:

```text
aigol/runtime/platform_core_execution_planning_service.py
```

ACLI Next now delegates read-only Worker handoff preview and execution plan preview generation to Platform Core.

ACLI Next remains responsible for:

- session interaction;
- request capture;
- delegation;
- rendering;
- confirmation capture;
- replay identifier presentation.

Platform Core now owns:

- read-only capability lookup;
- advisory authorization evidence;
- read-only Worker result summaries;
- execution plan construction;
- governance checkpoint synthesis;
- mutation preview generation;
- execution risk classification;
- replay plan construction.

No repository mutation, Git operation, deployment, provider invocation, write-capable Worker execution, or new authority layer is introduced.

## 2. Corrected Responsibility Map

| Responsibility | Previous Location | New Owner | Status |
| --- | --- | --- | --- |
| Read-only Worker capability lookup | ACLI Next `readonly_worker.py` | Platform Core service | Corrected |
| Read-only Worker authorization evidence | ACLI Next `readonly_worker.py` | Platform Core service | Corrected |
| Read-only Worker result summary | ACLI Next `readonly_worker.py` | Platform Core service | Corrected |
| Execution plan construction | ACLI Next `execution_plan.py` | Platform Core service | Corrected |
| Mutation preview generation | ACLI Next `execution_plan.py` | Platform Core service | Corrected |
| Governance checkpoint synthesis | ACLI Next `execution_plan.py` | Platform Core service | Corrected |
| Execution risk classification | ACLI Next `execution_plan.py` | Platform Core service | Corrected |
| Replay plan construction | ACLI Next `execution_plan.py` | Platform Core service | Corrected |
| CLI route parsing | ACLI Next / legacy CLI | ACLI Next / CLI adapter | Preserved |
| Rendering | ACLI Next | ACLI Next | Preserved |
| PGSP session delegation | ACLI Next bootstrap | ACLI Next adapter | Preserved |

## 3. Updated Dependency Diagram

Corrected runtime path:

```text
Human
-> ACLI Next
-> PGSP-governed interactive session
-> Platform Core execution planning service
   -> capability lookup
   -> advisory governance evidence
   -> execution plan preview
   -> mutation preview
   -> risk summary
   -> replay plan
-> ACLI Next rendering
-> Human
```

Interface reuse path:

```text
Web / REST / Mobile / Voice / ACLI Next
-> PGSP
-> Platform Core execution planning service
-> Replay-visible result
-> Interface rendering
```

The service accepts adapter-provided `command_name` and `runtime_version` values, allowing future interfaces to reuse the same Platform Core planning behavior without copying ACLI Next logic.

## 4. Implemented Runtime Surface

Files added:

| File | Purpose |
| --- | --- |
| `aigol/runtime/platform_core_execution_planning_service.py` | Canonical Platform Core service for read-only handoff previews and execution plan previews. |
| `tests/test_g8_platform_core_execution_planning_service.py` | Service reuse and ACLI thin-adapter guardrail tests. |
| `docs/governance/G8_06B_PLATFORM_CORE_EXECUTION_PLAN_PREVIEW_SERVICE_V1.md` | Governance implementation record. |

Files refactored:

| File | Purpose |
| --- | --- |
| `aigol/acli_next/readonly_worker.py` | Now delegates to Platform Core service and renders returned evidence. |
| `aigol/acli_next/execution_plan.py` | Now delegates to Platform Core service and renders returned evidence. |

No CLI behavior was removed. Existing `aigol next readonly-worker` and `aigol next execution-plan` routes remain intact.

## 5. Service Contract

The Platform Core service exposes:

| Function | Purpose |
| --- | --- |
| `run_platform_core_readonly_worker_handoff` | Builds read-only Worker handoff preview artifacts from confirmed session evidence. |
| `run_platform_core_execution_plan_preview` | Builds advisory execution plan, mutation preview, risk summary, governance checkpoints, and replay plan. |

Inputs:

- `session_id`;
- confirmed interactive session result;
- `created_at`;
- `replay_dir`;
- adapter `command_name`;
- adapter `runtime_version`;
- optional Worker sequence;
- optional requested capabilities;
- optional expected artifacts;
- optional potential repository impacts.

Outputs remain replay-visible dictionaries compatible with existing ACLI Next rendering and tests.

## 6. ACLI Next Refactor

ACLI Next modules now only:

- run or receive the interactive session result;
- call the Platform Core service;
- pass adapter command metadata;
- render returned fields.

Removed from ACLI Next:

- local capability registry;
- local read-only Worker summary construction;
- local advisory authorization evidence construction;
- local execution plan construction;
- local mutation preview construction;
- local risk summary logic;
- local governance checkpoint synthesis.

## 7. Governance Review

Governance ownership is improved.

The Platform Core service now emits advisory authorization evidence for:

- read-only Worker handoff previews;
- advisory execution plan previews.

The authorization evidence remains bounded:

- `execution_authorized: false`;
- `mutation_authorized: false`;
- `worker_dispatch_authorized: false`;
- `provider_authorized: false`;
- no approval creation;
- no execution authorization creation.

ACLI Next no longer creates the authorization vocabulary itself.

## 8. Replay Review

Replay behavior remains append-only and reconstructable.

The Platform Core service writes the same replay-visible artifact sequence used by prior G8-05 and G8-06 behavior:

- read-only Worker request/result/completion artifacts;
- execution plan request/plan/mutation-preview/completion artifacts.

The service records:

- `platform_core_service_version`;
- interactive replay reference;
- interactive replay hash;
- replay plan;
- artifact hashes.

ACLI Next presents replay identifiers but does not construct replay plans.

## 9. Compatibility Review

Existing behavior is preserved:

- `aigol next readonly-worker` still works;
- `aigol next execution-plan` still works;
- runtime outputs retain existing top-level statuses;
- tests for G8-03 through G8-06 remain valid;
- no mutating path is introduced.

New behavior:

- outputs include `platform_core_service_version`;
- source guardrail tests verify ACLI Next no longer owns planning logic.

## 10. Remaining Gaps

Remaining future work:

- migrate read-only Worker result generation to concrete Worker Platform runtimes if richer inspection is required;
- expose the Platform Core service through PGSP as a public contract for Web, REST, Mobile, and Voice adapters;
- add formal conformance tests preventing future capability registries inside human-interface adapters;
- certify any future mutating execution plan separately.

These are not blockers for the G8-06B correction.

## 11. Validation Strategy

Required validation:

```text
git diff --check
python -m py_compile aigol/runtime/platform_core_execution_planning_service.py aigol/acli_next/execution_plan.py aigol/acli_next/readonly_worker.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py tests/test_g8_acli_next_execution_plan.py tests/test_g8_platform_core_execution_planning_service.py
```

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/platform_core_execution_planning_service.py aigol/acli_next/execution_plan.py aigol/acli_next/readonly_worker.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py tests/test_g8_acli_next_execution_plan.py tests/test_g8_platform_core_execution_planning_service.py
```

Validation result: clean. Targeted pytest result: 17 passed.

## 12. Completion Criteria

| Criterion | Status |
| --- | --- |
| Platform Core execution planning service exists. | Complete |
| Capability lookup moved out of ACLI Next. | Complete |
| Execution plan construction moved out of ACLI Next. | Complete |
| Governance checkpoint synthesis moved out of ACLI Next. | Complete |
| Mutation preview generation moved out of ACLI Next. | Complete |
| Risk classification moved out of ACLI Next. | Complete |
| Replay plan construction moved out of ACLI Next. | Complete |
| ACLI Next delegates to Platform Core service. | Complete |
| Existing runtime behavior preserved. | Complete |
| Service is reusable by future interfaces. | Complete |
| No mutation, Git, provider, deployment, or write-capable Worker path introduced. | Complete |

## 13. Final Determination

G8-06B canonicalizes execution planning behind Platform Core and restores ACLI Next to a thin adapter role for execution planning and read-only handoff preview behavior.

Final verdict: PLATFORM_CORE_EXECUTION_PLANNING_CANONICALIZED
