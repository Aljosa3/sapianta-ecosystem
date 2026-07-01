# G8-06D Platform Core Execution Planning Service Refactoring V1

Status: Platform Core execution planning service refactored.

Final verdict: PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_REFACTORED

## 1. Executive Summary

G8-06D refactors the Platform Core execution planning service after the G8-06C boundary review found that the service was reusable but internally too centralized.

The refactoring preserves existing runtime behavior while decomposing responsibility into Platform Core owner surfaces:

- canonical capability lookup;
- Governance preview evidence;
- Replay preview planning and persistence;
- Worker Platform read-only preview evidence;
- OCS-owned advisory execution plan and mutation preview construction.

The public service remains:

- reusable by ACLI Next, Web, REST, Mobile, Voice, and future adapters;
- non-mutating;
- replay-visible;
- fail-closed;
- thin over internal Platform Core owner helpers;
- free of provider invocation, repository mutation, Git operation, deployment, and write-capable Worker execution.

## 2. Responsibility Decomposition

| Responsibility | Previous location | Refactored owner | Runtime artifact |
| --- | --- | --- | --- |
| Read-only capability lookup | `platform_core_execution_planning_service.py` | Canonical Capability Lookup | `aigol/runtime/platform_core_capability_lookup.py` |
| Read-only Worker authorization evidence | `platform_core_execution_planning_service.py` | Governance | `aigol/runtime/platform_core_governance_preview.py` |
| Advisory execution plan authorization evidence | `platform_core_execution_planning_service.py` | Governance | `aigol/runtime/platform_core_governance_preview.py` |
| Governance checkpoint list | `platform_core_execution_planning_service.py` | Governance | `aigol/runtime/platform_core_governance_preview.py` |
| Execution risk classification | `platform_core_execution_planning_service.py` | Governance policy preview | `aigol/runtime/platform_core_governance_preview.py` |
| Read-only Worker result summary | `platform_core_execution_planning_service.py` | Worker Platform preview | `aigol/runtime/platform_core_worker_preview.py` |
| Read-only Worker result validation | `platform_core_execution_planning_service.py` | Worker Platform preview | `aigol/runtime/platform_core_worker_preview.py` |
| Execution plan artifact construction | `platform_core_execution_planning_service.py` | OCS execution preview | `aigol/runtime/platform_core_ocs_execution_preview.py` |
| Mutation preview artifact construction | `platform_core_execution_planning_service.py` | OCS execution preview | `aigol/runtime/platform_core_ocs_execution_preview.py` |
| Replay plan construction | `platform_core_execution_planning_service.py` | Replay preview | `aigol/runtime/platform_core_replay_preview.py` |
| Replay artifact persistence | `platform_core_execution_planning_service.py` | Replay preview | `aigol/runtime/platform_core_replay_preview.py` |
| Service sequencing and assembly | `platform_core_execution_planning_service.py` | Execution planning service | Remains in `aigol/runtime/platform_core_execution_planning_service.py` |

## 3. Delegation Map

Current runtime path:

```text
Human interface
  |
  v
Platform Core execution planning service
  |
  +--> Canonical Capability Lookup
  |
  +--> Governance Preview
  |
  +--> Worker Platform Preview
  |
  +--> OCS Execution Preview
  |
  +--> Replay Preview
  |
  v
Replay-visible advisory result
```

The execution planning service now coordinates these helpers instead of constructing all planning, authorization, capability, risk, Worker, and replay evidence directly.

## 4. Dependency Updates

Files added:

| File | Purpose |
| --- | --- |
| `aigol/runtime/platform_core_capability_lookup.py` | Canonical read-only capability lookup surface for G8 previews. |
| `aigol/runtime/platform_core_governance_preview.py` | Governance evidence, confirmation checks, checkpoint synthesis, and risk classification. |
| `aigol/runtime/platform_core_replay_preview.py` | Replay plan generation and append-only preview artifact persistence. |
| `aigol/runtime/platform_core_worker_preview.py` | Read-only Worker result and summary preview. |
| `aigol/runtime/platform_core_ocs_execution_preview.py` | Advisory execution plan and descriptive mutation preview artifact construction. |

Files changed:

| File | Change |
| --- | --- |
| `aigol/runtime/platform_core_execution_planning_service.py` | Refactored into coordinator over Platform Core owner helpers. |
| `tests/test_g8_platform_core_execution_planning_service.py` | Added boundary guardrail test proving delegated owner responsibilities are no longer local service implementations. |

No ACLI Next adapter API change was required.

## 5. Refactoring Summary

The refactoring preserves the existing public calls:

- `run_platform_core_readonly_worker_handoff`;
- `run_platform_core_execution_plan_preview`.

The service still:

- validates and normalizes request parameters;
- sequences request, result, preview, and completion artifacts;
- assembles returned artifacts into the existing result shape;
- preserves fail-closed behavior;
- persists replay-visible artifacts through Replay preview helper delegation.

The service no longer owns:

- read-only capability lookup tables;
- governance authorization builders;
- read-only Worker result builders;
- execution plan artifact builders;
- mutation preview artifact builders;
- replay plan construction;
- governance checkpoint construction;
- execution risk classification.

## 6. Governance Impact

Governance impact: preserved and improved.

The previous implementation already avoided new external authority layers, but the service itself had begun centralizing Governance-like preview responsibilities. G8-06D moves those responsibilities into `platform_core_governance_preview.py`.

The refactoring does not grant:

- execution authorization;
- mutation authorization;
- provider authorization;
- write-capable Worker authorization;
- approval authority.

Governance evidence remains advisory and non-mutating.

## 7. Replay Impact

Replay impact: preserved.

Replay remains the reconstruction authority. G8-06D does not introduce replay reconstruction logic. It moves replay plan construction and append-only preview persistence behind `platform_core_replay_preview.py`.

Replay artifacts remain:

- deterministic;
- append-only;
- hash-bound;
- explicitly non-mutating;
- compatible with existing G8-05 and G8-06 targeted tests.

## 8. Architecture Boundary Assessment

| Boundary | Result | Notes |
| --- | --- | --- |
| ACLI Next thin entrypoint | Preserved | ACLI Next still delegates to Platform Core service. |
| Platform Core service coordination | Preserved | Service now assembles delegated results. |
| OCS ownership | Improved | Execution plan and mutation preview construction moved into OCS preview helper. |
| Governance ownership | Improved | Authorization, checkpoints, and risk classification moved into Governance preview helper. |
| Replay ownership | Improved | Replay plan and persistence moved into Replay preview helper. |
| Worker Platform ownership | Improved | Read-only Worker result preview moved into Worker preview helper. |
| Capability lookup ownership | Improved | Capability lookup table moved out of execution planning service. |
| Provider boundary | Preserved | No provider invocation added. |
| Mutation boundary | Preserved | No repository mutation, Git command, commit, or deployment added. |

## 9. Remaining Gaps

Known gaps remain intentionally visible:

- helper modules are preview owner surfaces, not full mature subsystems;
- capability lookup remains a small G8 preview lookup and should later bind to certified canonical projection records;
- Governance preview does not replace full Governance certification;
- OCS preview does not execute or dispatch;
- Worker preview does not invoke write-capable Workers;
- Replay preview does not reconstruct replay.

These gaps do not block G8-06D because the milestone is a boundary correction refactor, not full mutating execution.

## 10. Future Guardrails

Future milestones must preserve:

- human interfaces as thin adapters;
- execution planning service as coordinator only;
- Governance as policy and authorization authority;
- OCS as proposal and orchestration owner;
- Replay as reconstruction authority;
- Worker Platform as Worker capability and execution owner;
- Canonical Platform Knowledge as canonical capability lookup owner.

Future mutating execution must not be added to `platform_core_execution_planning_service.py` directly. It must be routed through OCS, Governance, Replay, Worker Platform, and certified mutation authorization surfaces.

## 11. Validation

Validation performed:

```text
git diff --check
python -m py_compile aigol/runtime/platform_core_execution_planning_service.py aigol/runtime/platform_core_capability_lookup.py aigol/runtime/platform_core_governance_preview.py aigol/runtime/platform_core_replay_preview.py aigol/runtime/platform_core_worker_preview.py aigol/runtime/platform_core_ocs_execution_preview.py aigol/acli_next/execution_plan.py aigol/acli_next/readonly_worker.py aigol/acli_next/__init__.py aigol/cli/aigol_cli.py
python -m pytest tests/test_g8_acli_next_bootstrap.py tests/test_g8_acli_next_interactive_session.py tests/test_g8_acli_next_readonly_worker_handoff.py tests/test_g8_acli_next_execution_plan.py tests/test_g8_platform_core_execution_planning_service.py
```

Validation result: clean.

## 12. Final Determination

The Platform Core execution planning service has been refactored into a thin coordination layer over Platform Core owner helpers.

The refactoring preserves existing ACLI Next behavior while preventing the service from becoming a second orchestration or governance engine.

Final verdict: PLATFORM_CORE_EXECUTION_PLANNING_SERVICE_REFACTORED
