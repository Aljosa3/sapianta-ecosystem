# G39-01 — IVE-2 Certification Evidence

Status: RECORDED

Date: 2026-07-28

## Evidence Subject

This evidence covers the planning-only
`INTELLIGENT_VALIDATION_ENGINE_V2` capability.

## Runtime Evidence

- G38 source artifacts are validated and replay-reconstructed before
  scheduling.
- The complete nested IVE-1 dependency model is validated.
- Requirements are grouped without changing requirement content.
- Topological waves are deterministic.
- Parallel waves contain only same-namespace groups with no dependency path in
  either direction.
- Full regression remains a final sequential barrier.
- Unknown dependencies fail closed with zero concurrency.
- Human Approval remains pending and exact-candidate-hash bound.
- No validation, pytest, Authorization, Worker, Provider, AiCLI, or mutation
  path is invoked.

## Deterministic Test Evidence

Focused IVE-2 suite:

```text
python -m pytest tests/test_g39_01_intelligent_validation_engine_v2.py -q

8 passed in 0.57s
```

IVE-2 plus G38, IVE-1, and IVE-0:

```text
python -m pytest \
  tests/test_g39_01_intelligent_validation_engine_v2.py \
  tests/test_g38_01_intelligent_validation_entry_integration.py \
  tests/test_g37_01_intelligent_validation_engine_v1.py \
  tests/test_g36_01_intelligent_validation_engine_v0.py -q

32 passed in 0.98s
```

Additional focused compatibility, compilation, diff, and conformance results
are:

```text
python -m pytest \
  tests/test_g39_01_intelligent_validation_engine_v2.py \
  tests/test_g38_01_intelligent_validation_entry_integration.py \
  tests/test_g37_01_intelligent_validation_engine_v1.py \
  tests/test_g36_01_intelligent_validation_engine_v0.py \
  tests/test_g27_05_platform_change_impact_analysis_runtime.py \
  tests/test_g27_07_platform_validation_planning_runtime.py \
  tests/test_g27_09_platform_validation_plan_candidate_composition_runtime.py \
  tests/test_g8_governed_validation_runtime.py \
  tests/test_g9_governed_validation_suite_runtime.py \
  tests/test_g15_governance_01_platform_capability_certification_registry.py \
  tests/test_g28_02_certified_capability_invocation_binding_runtime.py \
  tests/test_g14_30_canonical_human_interface_runtime_entry_service_v1.py \
  tests/test_replay_chain_integrity_validation_v1.py \
  tests/test_cli_provider_success_stabilization_v1.py -q

124 passed in 3.01s
```

```text
python -m pytest tests/test_governance_conformance.py -q
5 passed in 0.03s
```

Changed Python compilation: PASS.

`git diff --check`: PASS.

Governance conformance engine:

```text
PARTIALLY_CONFORMANT
18 checks passed
2 checks failed
0 critical violations
```

The two findings remain the repository's pre-existing visible hook drift:

- root pre-commit hook absent;
- nested `sapianta_system` hook missing `promotion_gate_v02` and
  `check_layer_freeze`.

IVE-2 does not modify or conceal these findings. The repository-wide pytest
suite was not required or executed; certification is bounded to the complete
IVE chain and directly affected compatibility surfaces above.

## Replay Evidence

Tests verify:

- deterministic source, selection, and schedule binding;
- identical schedules for identical canonical inputs;
- immutable group, wave, independence, schedule, artifact, and wrapper hashes;
- replay recomputation of the complete schedule;
- rejection of replay tampering;
- terminal failure for unknown dependency kinds;
- absence of authority escalation.
