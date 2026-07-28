# G37-01 IVE-1 Certification Evidence

Status: CERTIFIED

Version: 1.0.0

Date: 2026-07-28

Scope: deterministic semantic validation selection only

## Evidence Claim

G37-01:

- consumes and validates certified IVE-0 plan evidence;
- derives dependencies only from declared canonical edges;
- distinguishes direct and transitive validation requirements;
- traverses capability and constitutional component dependencies
  deterministically and cycle-safely;
- records the exact dependency path and edge hashes for every transitive
  requirement;
- preserves IVE-0 full-regression, test-target, allowlist, handoff, and Human
  Approval requirements;
- creates no candidate or command;
- executes and parallelizes no validation;
- invokes no Authorization, Worker, Provider, AiCLI, or execution gate;
- modifies no Replay semantic, pytest behavior, or execution-spine owner.

## Evidence Surface

| Artifact | SHA-256 |
| --- | --- |
| IVE-1 runtime | `faab570b4af1a609524e3bcb9f9f508e552bfb85f7480626bec04f1c11a47e11` |
| IVE-1 deterministic certification suite | `5ab4929f713df3aa1d12e71f409ca4cf3da6db56a80c1566bc1e54c58d550347` |
| IVE-1 architecture report | `e0841091ea036883b12a79c1579d76add3800e69dd3ab6dfc287317ae14aaccc` |
| IVE-1 compatibility report | `b7f3f7a0fd7cb27e48708b380d1328af1e4088276ca5c31b5a287e89f54223bb` |

## Verification Results

| Verification | Result |
| --- | --- |
| Complete IVE-1 suite | 8 passed in 0.26s |
| Focused constitutional compatibility suite | 100 passed in 1.98s |
| Changed Python compilation | PASS |
| Diff whitespace/error check | PASS |
| Governance conformance engine | PARTIALLY_CONFORMANT; 18 passed; 2 failed; 0 critical violations |
| Dependency model determinism | PASS |
| Rehashed noncanonical model rejection | PASS |
| Direct/transitive distinction | PASS |
| Capability-composition propagation | PASS |
| Deterministic shortest-path selection | PASS |
| Source identity fail-closed behavior | PASS |
| Replay reconstruction and tamper detection | PASS |
| Human Approval bypass | NO |
| Validation execution or parallelization | NO |
| Authorization, Worker, or Provider invocation | NO |
| Repository mutation authorized | NO |

## Runtime Replay Family

Every IVE-1 selection writes:

```text
000_ive_0_plan_bound.json
001_semantic_validation_selection_recorded.json
```

Reconstruction revalidates the IVE-0 source and recomputes direct subjects,
transitive dependency closure, and selected requirements against the embedded
canonical dependency model.

## Known Baseline Condition

The Governance conformance engine continues to expose the known repository hook
drift. It reports zero critical violations. G37-01 neither modifies nor hides
that pre-existing partial-conformance state.

The repository-wide pytest suite was not executed. Certification is explicitly
bounded to the complete new suite and affected compatibility surfaces.

## Verdict

```text
IVE_1_CONSTITUTIONALLY_CERTIFIED
```
