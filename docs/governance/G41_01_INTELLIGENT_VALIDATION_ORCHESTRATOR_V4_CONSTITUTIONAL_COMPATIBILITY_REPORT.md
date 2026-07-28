# G41-01 — IVE-4 Constitutional Compatibility Report

Status: COMPATIBLE

Date: 2026-07-28

## Assessment

IVE-4 is an additive planning orchestration layer. It composes certified
artifacts without changing their producers or any execution boundary.

| Boundary | Compatibility finding |
| --- | --- |
| IVE-0 | Invoked unchanged through G38; exact artifact retained |
| IVE-1 | Invoked unchanged through G38; exact artifact retained |
| G38 | Single planning entry consumed unchanged |
| IVE-2 | Scheduling recommendation invoked and retained unchanged |
| IVE-3 | Invoked unchanged only when real failed-validation evidence exists |
| Human Approval | Still mandatory before execution; not recorded by IVE-4 |
| Validation runtime | Not imported, invoked, or modified |
| pytest | No command, collection, configuration, or execution change |
| Replay | Additive IVE-4 bindings; existing families unchanged |
| Authorization | Not invoked or modified |
| Worker | Not invoked or modified |
| Provider | Not invoked or modified |
| AiCLI/Human Interface | No route or presentation change |
| PCBV31 | Execution spine unchanged |
| Automatic repair | Prohibited |
| Repository mutation | Prohibited at runtime |

## Responsibility Separation

IVE-4 owns only:

- deterministic stage invocation order;
- orchestration-mode validation;
- exact artifact and hash binding;
- unified planning bundle production;
- bundle replay and reconstruction.

It does not duplicate impact analysis, dependency selection, schedule
recommendation, failure analysis, approval, authorization, execution, result
production, or repair.

## Initial and Failure Continuity

The two-mode model preserves semantic correctness:

- initial planning ends at IVE-2 because IVE-3 requires a real failed
  validation;
- failure revalidation starts from the same normalized change, reconstructs
  the same certified planning lineage, and invokes IVE-3 using exact failure
  evidence;
- no artificial result is introduced to satisfy a nominal all-stage call.

Both modes produce the same canonical bundle family and preserve explicit
stage applicability.

## Fail-Closed Continuity

Missing failure evidence, altered bindings, unknown dependencies, stage
failure, or tampered replay produces no reduced recommendation and retains the
full-regression requirement. No downstream execution is attempted.

## Source Impact

Added:

- `aigol/runtime/intelligent_validation_orchestrator_v4.py`;
- `tests/test_g41_01_intelligent_validation_orchestrator_v4.py`;
- G41-01 governance, compatibility, certification, and evidence artifacts.

Metadata-only addition:

- `INTELLIGENT_VALIDATION_ORCHESTRATOR_V4` in the Platform Capability
  Certification Registry.

No IVE-0, IVE-1, G38, IVE-2, IVE-3, pytest, validation execution, Replay
protocol, Authorization, Worker, Provider, AiCLI, Human Interface, or PCBV31
source is modified.

## Verdict

```text
CONSTITUTIONAL_COMPATIBILITY_CONFIRMED
```

