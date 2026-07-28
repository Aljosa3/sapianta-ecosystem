# G40-01 — IVE-3 Constitutional Compatibility Report

Status: COMPATIBLE

Date: 2026-07-28

## Assessment

IVE-3 is an additive analysis layer over immutable planning and execution
evidence. It does not alter the planning chain or validation runtime.

| Boundary | Compatibility finding |
| --- | --- |
| IVE-0 | Artifact and replay consumed unchanged |
| IVE-1 | Selection and dependency evidence consumed unchanged |
| G38 | Planning entry and replay consumed unchanged |
| IVE-2 | Schedule artifact and replay consumed unchanged |
| Human Approval | Historical approval verified; future approval still required |
| Validation runtime | Existing replay read only; execution unchanged |
| pytest | No command, configuration, collection, or execution change |
| Replay | Additive IVE-3 family; existing protocols unchanged |
| Authorization | Not invoked or modified |
| Worker | Historical evidence read only; no invocation |
| Provider | Not invoked or modified |
| AiCLI/Human Interface | No route or presentation change |
| PCBV31 | Execution spine unchanged |
| Automatic repair | Prohibited |
| Repository mutation | Prohibited |

## Responsibility Separation

IVE-3 owns:

- deterministic lineage reconstruction;
- exact failed-group evidence binding;
- earliest known planning-boundary classification;
- dependency-descendant re-validation recommendation;
- failure-analysis replay.

It does not duplicate planning, scheduling, approval, authorization,
validation execution, result production, or repair.

## Fail-Closed Continuity

Unknown dependency, missing association, altered lineage, unsupported result
status, invalid approval, or tampered Replay blocks analysis. No reduced scope
is emitted and full regression remains required.

## Source Impact

Added:

- `aigol/runtime/intelligent_validation_engine_v3.py`;
- `tests/test_g40_01_intelligent_validation_engine_v3.py`;
- G40-01 governance and certification evidence.

Metadata-only addition:

- `INTELLIGENT_VALIDATION_ENGINE_V3` in the Platform Capability Certification
  Registry.

No IVE-0, IVE-1, G38, IVE-2, pytest, validation execution, Replay protocol,
Authorization, Worker, Provider, AiCLI, Human Interface, or PCBV31 source is
modified.

## Verdict

```text
CONSTITUTIONAL_COMPATIBILITY_CONFIRMED
```

