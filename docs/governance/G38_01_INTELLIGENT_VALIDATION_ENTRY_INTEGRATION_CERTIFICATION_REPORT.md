# G38-01 — Constitutional Certification Report

Status: CONSTITUTIONALLY CERTIFIED

Date: 2026-07-28

## Certification Scope

This report covers:

- the single development-validation planning entry;
- unchanged IVE-0 and IVE-1 consumption;
- deterministic planning-entry generation;
- immutable nested replay and reconstruction;
- fail-closed source and lineage validation;
- Human Approval continuity;
- G27, validation runtime, Replay, Authorization, Worker, Provider, AiCLI, and
  PCBV31 compatibility.

## Static Assessment

| Invariant | Assessment |
| --- | --- |
| Canonical normalized-change binding | PASS |
| IVE-0 output unchanged | PASS |
| IVE-1 output unchanged | PASS |
| Direct/transitive selection preserved | PASS |
| Full-regression policy never reduced | PASS |
| Existing G27-09 handoff preserved | PASS |
| Human Approval required before execution | PASS |
| Candidate construction prohibited | PASS |
| Validation execution prohibited | PASS |
| Replay lineage deterministic | PASS |
| Authorization/Worker/Provider/AiCLI unchanged | PASS |
| PCBV31 execution spine unchanged | PASS |

## Validation Evidence

The certification evidence is recorded at:

- `.github/governance/evidence/G38_01_INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_CERTIFICATION_EVIDENCE.md`.

| Validation | Result |
| --- | --- |
| G38-01 plus IVE-0 and IVE-1 | `24 passed in 0.51s` |
| Focused integration and compatibility suite | `116 passed in 2.51s` |
| Governance conformance tests | `5 passed in 0.03s` |
| Changed Python compilation | PASS |
| `git diff --check` | PASS |
| Governance conformance engine | `PARTIALLY_CONFORMANT`; 18 passed, 2 failed, 0 critical |

The conformance engine continues to expose the repository's known pre-existing
hook drift: the root pre-commit hook is absent and the nested
`sapianta_system` hook lacks `promotion_gate_v02` and `check_layer_freeze`.
G38-01 does not modify or conceal that limitation.

The repository-wide pytest suite was not required or executed. Certification
is bounded to the focused integration and directly affected compatibility
surfaces recorded in the evidence.

## Scope Boundary

This certification does not claim that every semantic validation requirement
has an executable allowlist mapping. It certifies the deterministic planning
entry and its fail-closed handoff to the existing execution pipeline.

## Final Verdict

The integrated entry reaches the unchanged G27 candidate boundary only through
certified IVE evidence, preserves explicit Human Approval, and grants no
execution authority.

```text
INTELLIGENT_VALIDATION_ENTRY_INTEGRATION_CONSTITUTIONALLY_CERTIFIED
```
