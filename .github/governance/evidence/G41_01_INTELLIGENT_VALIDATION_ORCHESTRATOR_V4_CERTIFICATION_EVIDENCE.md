# G41-01 — IVE-4 Certification Evidence

Status: RECORDED

Date: 2026-07-28

## Evidence Subject

This evidence covers the planning-only
`INTELLIGENT_VALIDATION_ORCHESTRATOR_V4` capability.

## Runtime Evidence

- Initial mode invokes G38, IVE-0, IVE-1, and IVE-2 unchanged.
- Initial mode records IVE-3 as not applicable without fabricated failure
  evidence.
- Failure mode invokes the complete unchanged chain through IVE-3.
- Exact nested certified artifacts and hashes are retained.
- One immutable bundle records stage applicability and current recommendation.
- Identical inputs produce identical bundles.
- Missing, mismatched, or tampered evidence fails closed.
- Human Approval remains required and unrecorded.
- No validation execution, dispatch, runtime parallelization, or automatic
  repair occurs.

## Deterministic Test Evidence

Focused IVE-4 suite:

```text
python -m pytest tests/test_g41_01_intelligent_validation_orchestrator_v4.py -q

10 passed in 1.17s
```

Complete IVE-0 through IVE-4 chain:

```text
python -m pytest \
  tests/test_g41_01_intelligent_validation_orchestrator_v4.py \
  tests/test_g40_01_intelligent_validation_engine_v3.py \
  tests/test_g39_01_intelligent_validation_engine_v2.py \
  tests/test_g38_01_intelligent_validation_entry_integration.py \
  tests/test_g37_01_intelligent_validation_engine_v1.py \
  tests/test_g36_01_intelligent_validation_engine_v0.py -q

51 passed in 3.31s
```

Focused constitutional compatibility suite:

```text
131 passed in 4.18s
```

Additional static and governance validation:

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

IVE-4 neither modifies nor conceals these findings. The repository-wide pytest
suite was not required or executed; certification is bounded to the complete
IVE chain and directly affected compatibility surfaces.

## Replay Evidence

Tests verify:

- immutable seven-step IVE-4 replay;
- deterministic bundle reconstruction;
- exact normalized-change, IVE-0, IVE-1, G38, IVE-2, and IVE-3 bindings;
- explicit stage invocation status;
- initial IVE-3 non-applicability;
- failure-mode IVE-3 invocation with real governed validation evidence;
- Human Approval continuity;
- rejection of replay tampering;
- absence of execution, mutation, and repair authority.
