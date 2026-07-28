# G37-01 — IVE-1 Constitutional Compatibility Report

Status: COMPATIBILITY VERIFIED

Date: 2026-07-28

## Finding

IVE-1 is an additive planning consumer of certified IVE-0 evidence.

It changes no IVE-0 artifact, impact rule, classification rule, recommendation,
or replay format. It changes no PCBV31 execution-spine component.

## Boundary Matrix

| Boundary | G37-01 effect |
| --- | --- |
| IVE-0 | Read-only validated source; unchanged |
| PCBV31 execution spine | Unchanged |
| G27 impact/planning/candidate composition | Unchanged |
| Human Approval | Still explicit and candidate-hash bound downstream |
| Authorization | Not called or modified |
| Replay | Existing immutable writer reused; semantics and ownership unchanged |
| Worker execution | Not called or modified |
| Provider execution | Not called or modified |
| AiCLI/Human Interface | No route or transport integration |
| pytest | No command, plugin, scheduler, or behavior change |
| Validation allowlist | Read-only carried references; no expansion |

## Dependency Authority

IVE-1 uses only:

- declared G20-03 capability-composition dependencies;
- the canonical Generation Certification evidence profile;
- immutable G37-01 constitutional component validation edges.

The cognition semantic relationship index is not used as an executable graph
because its certified contract prohibits that interpretation.

No import parsing, filename semantic inference, natural-language inference, or
probabilistic selection occurs.

## Failure Compatibility

Invalid IVE-0 artifacts, failed IVE-0 analysis, source identity mismatches,
altered dependency models, cycles, unknown model edges, malformed requirement
ordering, and replay tampering fail closed before candidate construction,
approval, authorization, or execution.

Failed selection requires full regression and cannot claim reduced scope.

## Compatibility Verdict

```text
IVE_1_CONSTITUTIONAL_COMPATIBILITY_PRESERVED
```
