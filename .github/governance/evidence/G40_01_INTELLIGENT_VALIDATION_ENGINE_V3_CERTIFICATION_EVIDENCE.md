# G40-01 — IVE-3 Certification Evidence

Status: RECORDED

Date: 2026-07-28

## Evidence Subject

This evidence covers the planning-only
`INTELLIGENT_VALIDATION_ENGINE_V3` capability.

## Runtime Evidence

- Complete IVE-0 through IVE-2 planning lineage is reconstructed.
- Governed validation candidate, Human Approval, result, and replay are
  validated.
- Direct failures resolve to IVE-0.
- Transitive failures resolve to IVE-1.
- Full-regression barrier failures resolve to IVE-2.
- Minimal re-validation includes exact failed requirements and dependency
  descendants only.
- Existing full-regression requirements remain terminal.
- Unknown bindings and dependencies fail closed.
- No validation execution or automatic repair occurs.

## Deterministic Test Evidence

Focused IVE-3 suite:

```text
python -m pytest tests/test_g40_01_intelligent_validation_engine_v3.py -q

9 passed in 1.33s
```

Additional IVE-chain compatibility, execution-boundary compatibility,
compilation, diff, and conformance results:

```text
python -m pytest \
  tests/test_g40_01_intelligent_validation_engine_v3.py \
  tests/test_g39_01_intelligent_validation_engine_v2.py \
  tests/test_g38_01_intelligent_validation_entry_integration.py \
  tests/test_g37_01_intelligent_validation_engine_v1.py \
  tests/test_g36_01_intelligent_validation_engine_v0.py -q

41 passed in 2.30s
```

```text
Focused constitutional compatibility suite:
133 passed in 4.74s
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

IVE-3 does not modify or conceal these findings. The repository-wide pytest
suite was not required or executed; certification is bounded to the complete
IVE chain and directly affected compatibility surfaces.

## Replay Evidence

Tests verify:

- immutable six-step IVE-3 replay;
- deterministic analysis for identical evidence;
- exact IVE-0, IVE-1, G38, and IVE-2 lineage;
- candidate-bound Human Approval evidence;
- result and validation replay binding;
- earliest-boundary evidence hashes;
- shortest dependency paths for re-validation;
- rejection of group, requirement, and replay tampering;
- absence of execution, mutation, and repair authority.
