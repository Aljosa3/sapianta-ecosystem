# G38-01 — Intelligent Validation Entry Integration Certification Evidence

Status: RECORDED

Date: 2026-07-28

## Evidence Subject

This evidence covers the additive
`INTELLIGENT_VALIDATION_ENTRY_INTEGRATION` Platform Core planning capability.

## Runtime Evidence

- Single canonical entry: `plan_development_validation(...)`.
- Canonical output:
  `INTELLIGENT_VALIDATION_PLANNING_ENTRY_ARTIFACT_V1`.
- Certified IVE-0 and IVE-1 functions are invoked without modification.
- Entry fields preserve IVE-1 selection, full-regression, handoff, and Human
  Approval objects exactly.
- Replay reconstruction validates both nested certified replay families.
- Failure is terminal before candidate construction, approval, Authorization,
  Worker, Provider, AiCLI, pytest, or repository mutation.

## Deterministic Test Evidence

Focused integration and engine compatibility:

```text
python -m pytest \
  tests/test_g38_01_intelligent_validation_entry_integration.py \
  tests/test_g37_01_intelligent_validation_engine_v1.py \
  tests/test_g36_01_intelligent_validation_engine_v0.py -q

24 passed in 0.51s
```

Additional compatibility, compilation, governance conformance, and diff
validation:

```text
python -m pytest \
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

116 passed in 2.51s
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

The two findings are the repository's pre-existing visible hook drift:

- root pre-commit hook absent;
- nested `sapianta_system` hook missing `promotion_gate_v02` and
  `check_layer_freeze`.

G38-01 does not modify or conceal these findings. The repository-wide pytest
suite was not required or executed; certification is bounded to the focused
integration and compatibility surfaces above.

## Replay Evidence

The deterministic test suite verifies:

- identical canonical inputs create identical entry artifacts;
- integrated IVE-0 and IVE-1 artifacts exactly equal independently generated
  certified artifacts;
- source mismatch fails closed before IVE handoff;
- wrapper tampering is rejected;
- nested IVE replay hashes and lineage reconstruct;
- no authority flag becomes true.

## Constitutional Boundary Evidence

The new runtime does not import:

- governed validation execution;
- validation Human Approval creation;
- Authorization;
- Workers;
- Providers;
- AiCLI;
- subprocess or pytest execution.

No existing execution, approval, authorization, replay protocol, Worker,
Provider, AiCLI, Human Interface, or PCBV31 source file is modified.
