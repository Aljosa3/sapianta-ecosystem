# G38-01 — Constitutional Compatibility Report

Status: COMPATIBLE

Date: 2026-07-28

## Assessment

G38-01 is an additive planning-entry integration. It composes the already
certified IVE-0 and IVE-1 functions and binds their immutable results. It does
not revise either engine or any downstream execution owner.

| Boundary | Compatibility finding |
| --- | --- |
| IVE-0 | Public function and artifact consumed unchanged |
| IVE-1 | Public function and artifact consumed unchanged |
| G27 impact/planning | Invoked only by unchanged IVE-0 policy |
| G27-09 candidate composition | Remains exclusive executable-candidate owner |
| Human Approval | Still downstream and exact-candidate-hash bound |
| Validation runtime | No import or behavioral change |
| pytest | No invocation, configuration, scheduling, or semantic change |
| Replay | Additive nested evidence only; protocol and ownership unchanged |
| Authorization | Not imported, invoked, or modified |
| Worker | Not imported, invoked, or modified |
| Provider | Not imported, invoked, or modified |
| AiCLI/Human Interface | No route, transport, or presentation change |
| PCBV31 execution spine | Unchanged |
| Repository mutation | Prohibited by artifact and authority flags |

## Source Impact

Added:

- `aigol/runtime/intelligent_validation_entry_integration_runtime.py`;
- `tests/test_g38_01_intelligent_validation_entry_integration.py`;
- G38-01 governance and certification evidence.

Metadata-only addition:

- `INTELLIGENT_VALIDATION_ENTRY_INTEGRATION` in the Platform Capability
  Certification Registry.

No certified IVE-0, IVE-1, G27, validation Governance, Authorization, Replay,
Worker, Provider, AiCLI, Human Interface, or pytest source was modified.

## Approval Continuity

G38-01 terminates before candidate creation. When an exact command mapping
exists, the unchanged G27-09 owner creates the candidate. Existing validation
Governance then requires explicit Human Approval bound to that candidate's
exact immutable hash. G38-01 neither records nor substitutes that decision.

## Replay Continuity

G38-01 adds a wrapper owned by the new entry module and references the
unchanged nested IVE replay families. Reconstruction calls both certified
reconstructors and verifies cross-family lineage. It does not append fields to
or reinterpret an existing replay artifact family.

## Compatibility Verdict

The integration is runtime-additive, planning-only, replay-visible,
non-authoritative, and compatible with the certified constitutional baseline.

```text
CONSTITUTIONAL_COMPATIBILITY_CONFIRMED
```

