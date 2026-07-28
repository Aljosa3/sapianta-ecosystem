# G36-01 — IVE-0 Constitutional Certification Report

Status: CONSTITUTIONALLY CERTIFIED

Date: 2026-07-28

## Certification Scope

This report certifies the planning-only IVE-0 surface:

- canonical normalized-change ingress;
- deterministic component discovery;
- deterministic constitutional classification;
- deterministic validation recommendation;
- immutable replay-visible evidence;
- fail-closed reconstruction;
- unchanged downstream approval and validation boundaries.

## Static Constitutional Assessment

| Invariant | Assessment |
| --- | --- |
| Deterministic input and output | PASS |
| Probabilistic/heuristic inference prohibited | PASS |
| Replay-visible immutable evidence | PASS |
| Human Approval required | PASS |
| Validation execution prohibited | PASS |
| Authorization unchanged | PASS |
| Worker and Provider execution unchanged | PASS |
| AiCLI and Human Interface unchanged | PASS |
| Existing validation pipeline unchanged | PASS |
| Fail-closed ambiguity and tamper handling | PASS |

## Validation Evidence

| Validation | Result |
| --- | --- |
| Complete IVE-0 deterministic suite | `9 passed in 0.14s` |
| IVE-0 plus G27-04/05/07/09, capability registry, existing single/suite validation, Governance conformance tests, and Replay chain integrity | `72 passed in 1.48s` |
| Changed Python module compilation | PASS |
| `git diff --check` | PASS |
| Governance conformance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 failed, 0 critical violations |

The conformance-engine result exposes the repository's known pre-existing hook
drift:

- root pre-commit hook absent;
- nested `sapianta_system` hook missing `promotion_gate_v02` and
  `check_layer_freeze` tokens.

G36-01 does not modify, conceal, or reclassify this baseline limitation.

The repository-wide pytest suite was not required or executed by this
generation. The certification claim is bounded to the complete IVE-0 suite and
the directly affected G27, registry, validation, Governance, and Replay
compatibility surfaces listed above.

## Remaining Limits

The limitations in
`docs/governance/G36_01_INTELLIGENT_VALIDATION_ENGINE_V0.md` remain
constitutional evidence. In particular, IVE-0 does not claim transitive
dependency inference or invent concrete test commands where structured mapping
metadata is absent.

## Final Verdict

The planning-only IVE-0 capability satisfies its bounded constitutional scope.
No execution, authorization, Worker, Provider, Replay-semantic, AiCLI, or
pytest behavior changed.

```text
IVE_0_CONSTITUTIONALLY_CERTIFIED
```
